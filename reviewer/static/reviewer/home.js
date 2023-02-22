console.log("hello world");

const csvBtn = document.getElementById("csv-btn");
const reportBtn = document.getElementById("report-btn");
const reportBtn_NLP = document.getElementById("report-btn-nlp");

const img = document.getElementById("img");
const img_nlp = document.getElementById("img-nlp");

const modalBody = document.getElementById("modal-body");
const reportForm = document.getElementById("report-form");
const alertBox = document.getElementById("alert-box");

const reportName = document.getElementById("id_name");
const reportRemarks = document.getElementById("id_remarks");
const csrf = document.getElementsByName("csrfmiddlewaretoken")[0].value;

const now = new Date();
const dateString = now
	.toLocaleString("ja-JP", {
		timeZone: "Asia/Tokyo",
		year: "numeric",
		month: "2-digit",
		day: "2-digit",
		hour: "2-digit",
		minute: "2-digit",
	})
	.replace(/\//g, "/");

const title = document.getElementById("title").textContent.replace(/^アプリ名： /, "") + " - " + dateString;

const handleAlerts = (type, msg) => {
	alertBox.innerHTML = `
        <div class="alert alert-${type}" role="alert">
            ${msg}
        </div>
    `;
};

if (img) {
	csvBtn.classList.remove("not-visible");
}

if (img) {
	reportBtn.classList.remove("not-visible");
}

if (img) {
	reportBtn_NLP.classList.remove("not-visible");
}

let selectedImg;

reportBtn.addEventListener("click", () => {
	// 画像が選択されたときの処理
	selectedImg = img;
});

reportBtn_NLP.addEventListener("click", () => {
	// NLP によって処理された画像が選択されたときの処理
	selectedImg = img_nlp;
});


function reportFormSubmitHandler(imgSrc, csrfToken, reportName, reportRemarks) {
	imgSrc = selectedImg;
	const name = reportName.value || title;


	return function (e) {
		e.preventDefault();
		const formData = new FormData();
		formData.append("csrfmiddlewaretoken", csrfToken);
		formData.append("name", name);
		formData.append("remarks", reportRemarks.value);
		formData.append("image", imgSrc.src);

		$.ajax({
			type: "POST",
			url: "/reports/save/",
			data: formData,
			success: function (response) {
				console.log(response);
				handleAlerts("success", "report created");
				reportForm.reset();
			},
			error: function (error) {
				console.log(error);
				handleAlerts("danger", "ups... something went wrong");
			},
			processData: false,
			contentType: false,
		});
	};
}

reportForm.addEventListener("submit", function submitHandler(e) {
	// イベントリスナーを一時的に解除する
	reportForm.removeEventListener("submit", submitHandler);

	// reportFormSubmitHandler 関数を呼び出す
	if (img.src) {
		reportFormSubmitHandler(img, csrf, reportName, reportRemarks)(e);
	} else if (img_nlp.src) {
		reportFormSubmitHandler(img_nlp, csrf, reportName, reportRemarks)(e);
	}

	// イベントリスナーを再度設定する
	reportForm.addEventListener("submit", submitHandler);
});

// reportBtnとreportBtn_NLPに対するイベントリスナーを設定する
reportBtn.addEventListener("click", () => {
	const existingImg = document.querySelector(".w-100");
	if (existingImg) {
		existingImg.remove();
	}

	const newImg = document.createElement("img");
	newImg.src = img.src;
	newImg.setAttribute("class", "w-100");
	modalBody.prepend(newImg);

	reportName.value = title; // nameフォームにtitleの値を設定する
});

reportBtn_NLP.addEventListener("click", () => {
	const existingImg = document.querySelector(".w-100");
	if (existingImg) {
		existingImg.remove();
	}

	const newImg = document.createElement("img");
	newImg.src = img_nlp.src;
	newImg.setAttribute("class", "w-100");
	modalBody.prepend(newImg);

	reportName.value = title; // nameフォームにtitleの値を設定する
});

// モーダルが閉じたときに、フォームをリセットする
$("#reportModal").on("hidden.bs.modal", function () {
	reportForm.reset();
	handleAlerts.reset();
});