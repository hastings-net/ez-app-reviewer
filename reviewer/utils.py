import uuid
import base64

# グラフ作成
import io
import plotly.io as pio
from io import BytesIO

# データ分析・形態素分析
import MeCab
import pandas as pd
import nlplot
import numpy as np
import matplotlib.pyplot as plt
from plotly.offline import plot


def generate_code():
    code = str(uuid.uuid4()).replace("-", "").upper()[:12]
    return code


def mecab_text(text):
    # MeCabのインスタンスを作成（辞書はmecab-ipadic-neologdを使用）
    # dicdir = "-d ./reviewer/mecab/dic/mecab-unidic-neologd"
    # dicdir = "-d /django/reviewer/mecab/dic/mecab-unidic-neologd"
    dicdir = "-d /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd"
    mecab = MeCab.Tagger(dicdir)

    # 形態素解析
    node = mecab.parseToNode(text)

    # 形態素解析した結果を格納するリスト
    wordlist = []

    while node:
        # 名詞のみリストに格納する
        if node.feature.split(",")[0] == "名詞":
            wordlist.append(node.surface)
        # 形容詞を取得、elifで追加する
        elif node.feature.split(",")[0] == "形容詞":
            wordlist.append(node.surface)
        # 動詞を取得、elifで追加する
        # elif node.feature.split(',')[0] == '動詞':
        #    wordlist.append(node.surface)
        node = node.next
    return wordlist


def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode("utf-8")
    buffer.close()
    return graph


def get_chart(chart_type, df_bush, **kwargs):
    plt.switch_backend("AGG")
    fig = plt.figure(figsize=(10, 4))

    df = df_bush[["at", "score", "content"]]

    # ユニーク値（score）のカウント
    df["score"].value_counts()

    # 日別でスコア数を表示する
    df_score = df[["at", "score"]]
    df_score = pd.crosstab(df["at"], df["score"], dropna=False)
    df_score = df_score.resample("D").sum()

    # 100%積み上げグラフで表示
    df_score_month = df_score.resample("M").sum()

    if chart_type == "#1":  # 折れ線グラフ
        print("折れ線グラフ")
        plt.switch_backend("AGG")
        df_score.plot()

    elif chart_type == "#2":  # 100%積み上げグラフ
        print("100%積み上げグラフ")

        # 正規化する
        df_score_month2 = df_score_month.div(df_score_month.sum(axis=1), axis=0)

        n_rows, n_cols = df_score_month2.shape
        positions = np.arange(n_rows)
        offsets = np.zeros(n_rows, dtype=df_score_month2.values.dtype)
        colors = plt.get_cmap("tab20c")(np.linspace(0, 1, n_cols))

        fig, ax = plt.subplots()
        ax.set_xticks(positions)
        ax.set_xticklabels([f"{x.strftime('%Y-%m')}" for x in df_score_month.index], rotation=0)

        for i in range(len(df_score_month2.columns)):
            # 棒グラフを描画する。
            bar = ax.bar(positions, df_score_month2.iloc[:, i], bottom=offsets, color=colors[i])
            offsets += df_score_month2.iloc[:, i]

            # 棒グラフのラベルを描画する。

            for rect in bar:
                cx = rect.get_x() + rect.get_width() / 2
                cy = rect.get_y() + rect.get_height() / 2
                ax.text(
                    cx,
                    cy,
                    df_score_month2.columns[i],
                    color="k",
                    ha="center",
                    va="center",
                )

    else:
        print("ups... failed to identify the chart type")

    plt.tight_layout()
    chart = get_graph()
    return chart


def get_nlp_chart(chart_nlp_type, df_bush, samples_number, **kwargs):
    # 形態素解析のためのデータフレームを作成
    df_nlp = df_bush[["at", "content"]]
    df_nlp = df_nlp[["content"]]
    df_nlp = df_nlp.rename(columns={"content": "text"})

    # Mecabでレビューの形態素解析を行う
    df_nlp["words"] = df_nlp["text"].apply(mecab_text)

    # nlplotで直近1カ月のレビューを可視化・分析
    npt = nlplot.NLPlot(df_nlp, target_col="words")

    # top_nで頻出上位単語, min_freqで頻出下位単語を指定
    stopwords = npt.get_stopword(top_n=0, min_freq=0)

    if chart_nlp_type == "#1":  # 頻出単語
        print("頻出単語")

        npt_ngram_bush = npt.bar_ngram(
            title="頻出単語 uni-gram",
            xaxis_label="word_count",
            yaxis_label="word",
            ngram=1,
            top_n=50,
            stopwords=stopwords,
        )

        npt_ngram = npt_ngram_bush.to_html(full_html=False)
        nlp_chart = npt_ngram

        image_bytes = npt_ngram_bush.to_image(format="png")
        nlp_chart_png = base64.b64encode(image_bytes).decode("utf-8")

    elif chart_nlp_type == "#2":  # 単語数の分布
        print("単語数の分布")

        npt_treemap_bush = npt.treemap(
            title="単語数の分布 Tree of Most Common Words",
            ngram=1,
            top_n=30,
            stopwords=stopwords,
        )

        npt_treemap = npt_treemap_bush.to_html(full_html=False)
        nlp_chart = npt_treemap

        image_bytes = npt_treemap_bush.to_image(format="png")
        nlp_chart_png = base64.b64encode(image_bytes).decode("utf-8")

    elif chart_nlp_type == "#3":  # ワードクラウド
        print("ワードクラウド")

        npt_wordcloud = npt.wordcloud(
            max_words=100,
            max_font_size=100,
            colormap="tab20_r",
            stopwords=stopwords,
        )

        plt.switch_backend("AGG")
        plt.imshow(npt_wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.tight_layout()
        npt_wordcloud = get_graph()
        nlp_chart_png = npt_wordcloud
        nlp_chart = None

    elif chart_nlp_type == "#4":  # 共起ネットワーク
        print("共起ネットワーク")

        node = 0
        samples_number = int(samples_number)

        if samples_number == 100:
            node = 5
        elif samples_number == 300:
            node = 10
        elif samples_number == 500:
            node = 15
        elif samples_number == 1000:
            node = 25

        npt.build_graph(stopwords=stopwords, min_edge_frequency=node)
        npt_network_bush = npt.co_network(
            title="共起ネットワーク Co-occurrence network",
            sizing=100,
            node_size="adjacency_frequency",
            color_palette="hls",
            width=1100,
            height=700,
            save=False,
        )

        npt_network_html = plot(npt_network_bush, output_type="div")
        nlp_chart = npt_network_html

        buffer = io.BytesIO()
        pio.write_image(npt_network_bush, buffer, format="png")
        image_bytes = buffer.getvalue()
        nlp_chart_png = base64.b64encode(image_bytes).decode("utf-8")

    else:
        print("ups... failed to identify the chart type")

    return nlp_chart, nlp_chart_png
