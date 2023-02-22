from django.shortcuts import render
from .forms import URLForm
from reports.forms import ReportForm
from .utils import (
    # home_viewの関数
    mecab_text,
    get_chart,
    get_nlp_chart,
)

# データ分析・形態素分析
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from google_play_scraper import Sort, reviews

# Authentication
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from io import StringIO
from django.http import HttpResponse

# Create your views here.


@login_required
def home_view(request):
    no_data = None
    df_bush = []

    form = URLForm(request.POST or None)
    report_form = ReportForm()

    if request.method == "POST":
        form = URLForm(request.POST)
        chart_type = request.POST.get("chart_type")
        chart_nlp_type = request.POST.get("chart_nlp_type")
        samples_number = request.POST.get("samples_number")

        if form.is_valid():
            # URLの取得
            url = form.cleaned_data["url"]

            # URLの検証
            if not url.startswith("https://play.google.com/store/apps/details?id="):
                form = URLForm(request.POST)
                no_data = "GooglePlayアプリストアのURLではありません。正しいURLを入力してください。"
                return render(request, "home.html", {"form": form, "no_data": no_data})

            app_id = url.split("=")[-1]

            # google_play_scraperでレビュー取得
            result, continuation_token = reviews(
                app_id,
                lang="ja",  # defaults to 'en'
                country="jp",  # defaults to 'us'
                sort=Sort.NEWEST,  # defaults to Sort.NEWEST
                count=int(samples_number),  # defaults to 100
            )

            # URLの検証
            if not result:
                form = URLForm(request.POST)
                no_data = "レビューを取得できませんでした。アプリにレビューがないか、URLが間違っている可能性があります。"
                return render(request, "home.html", {"form": form, "no_data": no_data})

            # アプリ情報の取得
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.find("title").text

            try:
                developer = soup.find("div", class_="Vbfug auoIOc").text
            except AttributeError:
                developer = "※※情報を取得できませんでした※※"

            try:
                img_tag = soup.find("img", class_="T75of cN0oRe fFmL2e")
                app_icon = img_tag.attrs.get("src")
            except AttributeError:
                img_tag = None
                app_icon = "※※情報を取得できませんでした※※"

            # 取得したレビューをデータフレームに格納
            df_bush = pd.DataFrame(np.array(result), columns=["review"])
            df_bush = df_bush.join(pd.DataFrame(df_bush.pop("review").tolist()))
            df = df_bush[["at", "score", "content"]]

            # ユニーク値（score）のカウント
            df["score"].value_counts()

            # 日別でスコア数を表示する
            df_score = df[["at", "score"]]
            df_score = pd.crosstab(df["at"], df["score"], dropna=False)
            df_score = df_score.resample("D").sum()

            # 月別で集計
            df_score_month = df_score.resample("M").sum()

            # 折れ線グラフ・100%積み上げ棒グラフの作成
            chart2 = get_chart(chart_type, df_bush)

            # 形態素解析のためのデータフレームを作成
            df_nlp = df_bush[["at", "content"]]
            df_nlp = df_nlp[["content"]]
            df_nlp = df_nlp.rename(columns={"content": "text"})

            # 形態素結果をリスト化し、データフレームdf1に結果を列追加する
            df_nlp["words"] = df_nlp["text"].apply(mecab_text)

            # 形態素解析グラフの作成
            nlp_chart, nlp_chart_png = get_nlp_chart(chart_nlp_type, df_bush, samples_number)

            # 「#3：共起ネットワーク」の場合の処理
            if chart_nlp_type == "#3":
                nlp_chart_png = nlp_chart_png
                nlp_wordcloud_png = nlp_chart_png
            else:
                nlp_wordcloud_png = None

            df = df.to_html()
            df_score = df_score.to_html()
            df_score_month = df_score_month.to_html()
            df_nlp = df_nlp.to_html()

            # 「スコア推移」の場合の処理
            if chart_type == "#1":
                df_score = df_score
                df_score_month = None
            else:
                df_score = None
                df_score_month = df_score_month

            context = {
                "form": form,
                "report_form": report_form,
                "url": url,
                "app_id": app_id,
                "app_icon": app_icon,
                "title": title,
                "developer": developer,
                "df": df,
                "df_score": df_score,
                "df_score_month": df_score_month,
                "chart2": chart2,
                "df_nlp": df_nlp,
                "nlp_chart": nlp_chart,
                "nlp_chart_png": nlp_chart_png,
                "nlp_wordcloud_png": nlp_wordcloud_png,
            }

            return render(request, "home.html", context)

    else:
        form = URLForm(request.POST or None)

    return render(request, "home.html", {"form": form, "no_data": no_data})


def download_csv(request):
    url = request.GET.get("url")
    # samples_number = request.GET.get("samples_number")
    app_id = url.split("=")[-1]

    # google_play_scraperでレビュー取得
    result, continuation_token = reviews(
        app_id,
        lang="ja",  # defaults to 'en'
        country="jp",  # defaults to 'us'
        sort=Sort.NEWEST,  # defaults to Sort.NEWEST
        count=1000,  # defaults to 100
    )

    # 取得したレビューをデータフレームに格納
    df_bush = pd.DataFrame(np.array(result), columns=["review"])
    df_bush = df_bush.join(pd.DataFrame(df_bush.pop("review").tolist()))
    df = df_bush[["at", "score", "content"]]

    # CSVのエンコーディングを指定してファイルを作成
    csvfile = StringIO()
    df.to_csv(csvfile, index=False, escapechar="\\")
    csvfile.seek(0)  # ファイルポインタを先頭に戻す
    csv_text = csvfile.getvalue().encode("utf-8")

    # レスポンスの作成
    response = HttpResponse(csv_text, content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="data.csv"'
    return response


# class SaleListView(LoginRequiredMixin, ListView):
#     model = Sale
#     template_name = "reviewer/main.html"
#     context_object_name = "qs"


# class SaleDetailView(LoginRequiredMixin, DetailView):
#     model = Sale
#     template_name = "reviewer/detail.html"
