from django import forms


CHART_CHOICES = (
    ("#1", "スコア推移：折れ線グラフ"),
    ("#2", "スコア推移：100%積み上げ棒グラフ"),
)

CHART_NLP_CHOICES = (
    ("#1", "形態素解析：頻出単語"),
    ("#2", "形態素解析：単語数の分布"),
    ("#3", "形態素解析：ワードクラウド"),
    ("#4", "形態素解析：共起ネットワーク"),
)


class URLForm(forms.Form):
    url = forms.CharField(
        label="URL",
        widget=forms.TextInput(attrs={"placeholder": "https://play.google.com/store/apps/details?id=●●●●●●●●●●●●●"}),
    )
    chart_type = forms.ChoiceField(label="表示するグラフの種類", choices=CHART_CHOICES)
    chart_nlp_type = forms.ChoiceField(label="形態素解析グラフの種類", choices=CHART_NLP_CHOICES)
    samples_number = forms.ChoiceField(
        label="サンプリング数", choices=[(100, "100件"), (300, "300件"), (500, "500件"), (1000, "1,000件")]
    )
