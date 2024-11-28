function updateVideoSource(params = {}) {
    const urlParams = new URLSearchParams(params).toString();
    const video = document.getElementById("videoBox");
    const videoUrl = document.getElementById("videoBox").dataset.videoUrl;
    video.src = `${videoUrl}?${urlParams}`;
}

function updateThreshold() {
    const thresholdCB = document.getElementById("thresholdToggle");

    const values = ['lowerH', 'upperH', 'lowerS', 'upperS', 'lowerV', 'upperV'].map(id => parseInt(document.getElementById(id).value));
    [0, 2, 4].forEach(i => {
        if (values[i] >= values[i + 1]) {
            values[i] = values[i + 1];
            document.getElementById([['lowerH', 'lowerS', 'lowerV'][i / 2]]).value = values[i];
        }
    });

    const ids = ['lowerH', 'upperH', 'lowerS', 'upperS', 'lowerV', 'upperV'];
    values.forEach((value, i) => document.getElementById(ids[i] + 'Value').innerText = value);

    const params = {
        lower_h: values[0],
        upper_h: values[1],
        lower_s: values[2],
        upper_s: values[3],
        lower_v: values[4],
        upper_v: values[5]
    };
    sendRequest("/change_threshold", params, (response, status) => {
        if (status === 200) {
            console.log(response);
        }
    });

    updateVideoSource({ threshold: thresholdCB.checked });
}

function updateScore() {
    const bScore = parseFloat(document.getElementById("bScore").value);
    const hScore = parseFloat(document.getElementById("hScore").value);
    const pcm = parseFloat(document.getElementById("pcm").value);

    const delay = parseFloat(document.getElementById("delay").value);

    if (bScore < -100) {
        document.getElementById("bScore").value = -100;
        document.getElementById("bScoreValue").innerText = -100;
    } else if (bScore > 100) {
        document.getElementById("bScore").value = 100;
        document.getElementById("bScoreValue").innerText = 100;
    } else {
        document.getElementById("bScoreValue").innerText = bScore;
    }

    if (hScore < -100) {
        document.getElementById("hScore").value = -100;
        document.getElementById("hScoreValue").innerText = -100;
    } else if (hScore > 100) {
        document.getElementById("hScore").value = 100;
        document.getElementById("hScoreValue").innerText = 100;
    } else {
        document.getElementById("hScoreValue").innerText = hScore;
    }

    if (pcm < 0) {
        document.getElementById("pcm").value = 0;
        document.getElementById("pcmValue").innerText = 0;
    } else if (pcm > 100) {
        document.getElementById("pcm").value = 100;
        document.getElementById("pcmValue").innerText = 100;
    } else {
        document.getElementById("pcmValue").innerText = pcm;
    }

    if (delay < 0) {
        document.getElementById("delay").value = 0;
    } else if (delay > 10) {
        document.getElementById("delay").value = 10;
    } else {
        document.getElementById("delay").value = delay;
    }

    document.getElementById('bScoreValue').innerText = bScore;
    document.getElementById('hScoreValue').innerText = hScore;
    document.getElementById('pcmValue').innerText = pcm;
    document.getElementById('delayValue').innerText = delay;

    sendRequest("/change_score", { b_score: bScore, h_score: hScore, pcm: pcm, delay: delay }, (response, status) => {
        if (status === 200) {
            console.log(response);
        }
    });
}

function updateCropSize() {
    const topCrop = document.getElementById("topCrop").value;
    const bottomCrop = document.getElementById("bottomCrop").value;
    const rightCrop = document.getElementById("rightCrop").value;

    document.getElementById("topCropValue").innerText = topCrop;
    document.getElementById("bottomCropValue").innerText = bottomCrop;
    document.getElementById("rightCropValue").innerText = rightCrop;

    sendRequest("/change_crop", { top_crop: topCrop, bottom_crop: bottomCrop, right_crop: rightCrop }, (response, status) => {
        if (status === 200) {
            console.log(response);
        }
    });
}

function toggleCropSource() {
    const referenceCB = document.getElementById("referenceToggle");
    const thresholdCB = document.getElementById("thresholdToggle");
    const cropCB = document.getElementById("cropToggle");

    const topCrop = document.getElementById("topCrop")
    const bottomCrop = document.getElementById("bottomCrop")
    const rightCrop = document.getElementById("rightCrop")

    if (cropCB.checked) {
        topCrop.disabled = false;
        bottomCrop.disabled = false;
        rightCrop.disabled = false;
    } else {
        topCrop.disabled = true;
        bottomCrop.disabled = true;
        rightCrop.disabled = true;
    }

    updateVideoSource({ threshold: thresholdCB.checked, reference: referenceCB.checked, crop_preview: cropCB.checked });
}

function toggleSource() {
    const referenceCB = document.getElementById("referenceToggle");
    const thresholdCB = document.getElementById("thresholdToggle");

    const ids = ['lowerH', 'upperH', 'lowerS', 'upperS', 'lowerV', 'upperV'];
    ids.forEach(id => document.getElementById(id).disabled = !thresholdCB.checked);

    updateVideoSource({ threshold: thresholdCB.checked, reference: referenceCB.checked});
}

function takeCalibrate() {
    document.getElementById("statusRendering").innerText = "Take Foto Calibration in Progress";

    sendRequest("/calibrate", {}, (response, status) => {
        if (status === 200) {
            console.log(response);
            document.getElementById("statusRendering").innerText = `Take Foto Calibration Complete | Folder Path: ${response}`;
        }
    });
}

function takeFile() {
    document.getElementById("statusRendering").innerText = "Take Foto File in Progress";

    sendRequest("/take_file", {}, (response, status) => {
        if (status === 200) {
            console.log(response);
            document.getElementById("statusRendering").innerText = `Take Foto File Complete | Folder Path: ${response}`;
        }
    });
}

function startScan() {
    document.getElementById("statusRendering").innerText = "Scanning in Progress";

    sendRequest("/scanning", {}, (response, status) => {
        if (status === 200) {
            console.log(response);
            document.getElementById("statusRendering").innerText = `Scanning Complete | Folder Path: ${response}`;
        }
    });
}

function startGenerate() {
    const folder_path = document.getElementById("folderPath").value;
    console.log(folder_path);

    document.getElementById("statusRendering").innerText = "Generating in Progress";

    sendRequest("/generate", { folder_path: folder_path }, (response, status) => {
        if (status === 200) {
            console.log(response);
            document.getElementById("statusRendering").innerText = `Generating Complete | Folder Path: ${response}`;
        }
    });
}

function startGenerateDebug() {
    const folder_path = document.getElementById("folderPathDebug").value;
    console.log(folder_path);

    document.getElementById("dataRenderingDebug").innerText = "Generating in Progress";

    sendRequest("/generate_debug", { folder_path: folder_path }, (response, status) => {
        if (status === 200) {
            console.log(response);
            document.getElementById("dataRenderingDebug").innerText = `${response}`;
        }
    });
}

function rotatingTest() {
    document.getElementById("statusRendering").innerText = "Rotating Test in Progress";
    sendRequest("/rotating_test", {}, (response, status) => {
        if (status === 200) {
            console.log(response);
            document.getElementById("statusRendering").innerText = "Rotating Test Complete";
        }
    });
}

function reset() {
    document.getElementById("statusRendering").innerText = "Reset in Progress";
    sendRequest("/reset", {}, (response, status) => {
        if (status === 200) {
            console.log(response);
            document.getElementById("statusRendering").innerText = "Reset Complete";
            location.reload();
        }
    });
}

function startData() {
    document.getElementById("dataRendering").innerText = "Data in Progress";

    const folder_path_cp = document.getElementById("folderPathCP").value;
    const x1data = document.getElementById("x1data").value;
    const x2data = document.getElementById("x2data").value;

    sendRequest("/data_gen", { folder_path_cp: folder_path_cp, x1data: x1data, x2data: x2data }, (response, status) => {
        if (status === 200) {
            console.log(response);
            document.getElementById("dataRendering").innerText = `Data Complete | ${response}`;
        }
    });
}

function startDataDebug() {
    document.getElementById("dataRenderingDebug").innerText = "Data in Progress";

    const folder_path = document.getElementById("folderPathDebug").value;
    console.log(folder_path);

    const x1data = document.getElementById("x1datad").value;
    const x2data = document.getElementById("x2datad").value;

    sendRequest("/data_gen_debug", { folder_path: folder_path, x1data: x1data, x2data: x2data }, (response, status) => {
        if (status === 200) {
            console.log(response);
            document.getElementById("dataRenderingDebug").innerText = `${response}`;
        }
    });
}

function sendRequest(url, params = {}, callback) {
    const xmlHttp = new XMLHttpRequest();
    const urlParams = new URLSearchParams(params).toString();
    xmlHttp.open("GET", `${url}?${urlParams}`, true);

    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState === 4) {
            callback(xmlHttp.responseText, xmlHttp.status);
        }
    };

    xmlHttp.send(null);
}