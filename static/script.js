document.getElementById("upload-form").onsubmit = async function(event) {
    event.preventDefault();
    
    let fileInput = document.getElementById("file-upload");
    let formData = new FormData();
    formData.append("file", fileInput.files[0]);

    let statusElement = document.getElementById("status");
    statusElement.innerText = "Uploading...";

    let response = await fetch("/upload", {
        method: "POST",
        body: formData
    });

    let result = await response.json();
    statusElement.innerText = result.message;
};
