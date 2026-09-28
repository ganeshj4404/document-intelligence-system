const loginForm = document.getElementById("login-form");
const loginMessage = document.getElementById("login-message");

const loginSection = document.getElementById("login-section");
const dashboardSection = document.getElementById("dashboard-section");

const logoutButton = document.getElementById("logout-button");
const refreshButton = document.getElementById("refresh-button");
const documentsList = document.getElementById("documents-list");
const documentFile = document.getElementById("document-file");
const uploadButton = document.getElementById("upload-button");
const uploadMessage = document.getElementById("upload-message");
const resultSection = document.getElementById("result-section");
const resultTitle = document.getElementById("result-title");
const resultContent = document.getElementById("result-content");

let currentAudioUrl = null;


// =========================
// LOGIN
// =========================

loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    loginMessage.textContent = "Logging in...";

    try {
        const formData = new URLSearchParams();

        formData.append("username", username);
        formData.append("password", password);

        const response = await fetch("/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Login failed");
        }

        localStorage.setItem("access_token", data.access_token);

        loginMessage.textContent = "Login successful!";

        loginSection.classList.add("hidden");
        dashboardSection.classList.remove("hidden");

        await loadDocuments();

    } catch (error) {
        loginMessage.textContent = error.message;
        console.error("Login error:", error);
    }
});


// =========================
// LOAD DOCUMENTS
// =========================

async function loadDocuments() {
    console.log("Loading documents...");

    const token = localStorage.getItem("access_token");

    if (!token) {
        console.error("No access token found.");

        documentsList.innerHTML =
            "<p>Please login again.</p>";

        return;
    }

    try {
        const response = await fetch("/documents", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Accept": "application/json"
            }
        });

        console.log(
            "Documents response status:",
            response.status
        );

        const data = await response.json();

        if (!response.ok) {
            if (response.status === 401) {
                localStorage.removeItem("access_token");

                loginSection.classList.remove("hidden");
                dashboardSection.classList.add("hidden");

                throw new Error(
                    "Session expired. Please login again."
                );
            }

            throw new Error(
                data.detail || "Failed to load documents"
            );
        }

        documentsList.innerHTML = "";

        if (data.length === 0) {
            documentsList.innerHTML =
                "<p>No documents found.</p>";

            return;
        }

        data.forEach(function (doc) {

            const documentCard =
                document.createElement("div");

            documentCard.className = "document-card";

            documentCard.innerHTML = `
                <h4>${doc.file_name}</h4>

                <p>
                    <strong>Status:</strong>
                    ${doc.status}
                </p>

                <p>
                    <strong>Validation:</strong>
                    ${doc.validation_status}
                </p>

                <p>
                    <strong>Summary Validation:</strong>
                    ${doc.summary_validation_status}
                </p>

                <p>
                    <strong>Created:</strong>
                    ${doc.created_at}
                </p>

                <p>
                    <strong>Processed:</strong>
                    ${doc.processed_at || "Not processed"}
                </p>

                <button
                    class="result-button"
                    data-action="summary"
                    data-id="${doc.id}">
                    View Summary
                </button>

                <button
                    class="result-button"
                    data-action="summary-audio"
                    data-id="${doc.id}">
                    Play Summary
                </button>

                <button
                    class="result-button"
                    data-action="paraphrase"
                    data-id="${doc.id}">
                    View Paraphrase
                </button>

                <button
                    class="result-button"
                    data-action="audio"
                    data-id="${doc.id}">
                    Play Audio
                </button>

                <button
                    class="result-button"
                    data-action="reprocess"
                    data-id="${doc.id}">
                    Reprocess
                </button>

                <button
                    class="result-button"
                    data-action="delete"
                    data-id="${doc.id}">
                    Delete
                </button>
            `;

            documentsList.appendChild(documentCard);
        });

    } catch (error) {

        console.error(
            "Error loading documents:",
            error
        );

        documentsList.innerHTML = `
            <p>
                Error loading documents:
                ${error.message}
            </p>
        `;
    }
}
// =========================
// UPLOAD & PROCESS
// =========================

uploadButton.addEventListener(
    "click",
    async function () {

        const file = documentFile.files[0];

        if (!file) {
            uploadMessage.textContent =
                "Please choose a document first.";
            return;
        }

        const token = localStorage.getItem("access_token");

        if (!token) {
            uploadMessage.textContent =
                "Please login again.";
            return;
        }

        uploadButton.disabled = true;
        uploadButton.textContent = "Processing...";
        uploadMessage.textContent =
            "Uploading and processing document...";

        try {

            const formData = new FormData();

            formData.append("file", file);

            const response = await fetch(
                "/documents/upload",
                {
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${token}`
                    },
                    body: formData
                }
            );

            const data = await response.json();

            if (!response.ok) {

                throw new Error(
                    data.detail || "Upload failed"
                );
            }

            uploadMessage.textContent =
                "Document processed successfully!";

            documentFile.value = "";

            await loadDocuments();

        } catch (error) {

            console.error(
                "Upload error:",
                error
            );

            uploadMessage.textContent =
                `Error: ${error.message}`;

        } finally {

            uploadButton.disabled = false;
            uploadButton.textContent =
                "Upload & Process";
        }
    }
);

// =========================
// REFRESH DOCUMENTS
// =========================

refreshButton.addEventListener(
    "click",
    async function () {

        console.log("Refresh button clicked.");

        refreshButton.disabled = true;
        refreshButton.textContent = "Refreshing...";

        await loadDocuments();

        refreshButton.disabled = false;
        refreshButton.textContent = "Refresh Documents";
    }
);


// =========================
// LOGOUT
// =========================

logoutButton.addEventListener(
    "click",
    function () {

        localStorage.removeItem("access_token");

        dashboardSection.classList.add("hidden");
        loginSection.classList.remove("hidden");

        documentsList.innerHTML = "";
        loginMessage.textContent = "";
    }
);
// =========================
// SHOW SUMMARY
// =========================

async function showSummary(documentId) {

    const token = localStorage.getItem("access_token");

    if (!token) {
        return;
    }

    resultSection.classList.remove("hidden");

    resultTitle.textContent = "Summary";
    resultContent.textContent = "Loading summary...";

    try {

        const response = await fetch(
            `/documents/${documentId}/summary`,
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        if (!response.ok) {
            const data = await response.json();
            throw new Error(
                data.detail || "Failed to load summary"
            );
        }

        const summary = await response.text();

        resultContent.textContent = summary;

    } catch (error) {

        resultContent.textContent =
            `Error: ${error.message}`;
    }
}


// =========================
// SHOW PARAPHRASE
// =========================

async function showParaphrase(documentId) {

    const token = localStorage.getItem("access_token");

    if (!token) {
        return;
    }

    resultSection.classList.remove("hidden");

    resultTitle.textContent = "Paraphrase";
    resultContent.textContent = "Loading paraphrase...";

    try {

        const response = await fetch(
            `/documents/${documentId}/paraphrase`,
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        if (!response.ok) {
            const data = await response.json();
            throw new Error(
                data.detail || "Failed to load paraphrase"
            );
        }

        const paraphrase = await response.text();

        resultContent.textContent = paraphrase;

    } catch (error) {

        resultContent.textContent =
            `Error: ${error.message}`;
    }
}


// =========================
// PLAY AUDIO
// =========================

async function playAudio(documentId) {

    const token = localStorage.getItem("access_token");

    if (!token) {
        return;
    }

    resultSection.classList.remove("hidden");

    resultTitle.textContent = "Full Document Audio";
    resultContent.textContent = "Loading audio...";

    try {

        const response = await fetch(
            `/documents/${documentId}/audio`,
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        if (!response.ok) {
            const data = await response.json();
            throw new Error(
                data.detail || "Failed to load audio"
            );
        }

        const audioBlob = await response.blob();

        // Remove previous temporary audio URL
        if (currentAudioUrl) {
            URL.revokeObjectURL(currentAudioUrl);
        }

        currentAudioUrl = URL.createObjectURL(audioBlob);

        const audioPlayer = document.createElement("audio");

        audioPlayer.controls = true;
        audioPlayer.src = currentAudioUrl;

        resultContent.innerHTML = "";
        resultContent.appendChild(audioPlayer);

    } catch (error) {

        resultContent.textContent =
            `Error: ${error.message}`;
    }
}
// =========================
// DOCUMENT RESULT BUTTONS
// =========================

documentsList.addEventListener("click", function (event) {

    const button = event.target.closest(".result-button");

    if (!button) {
        return;
    }

    const documentId = button.dataset.id;
    const action = button.dataset.action;

    console.log("Button clicked:", action, "Document:", documentId);

    if (action === "summary") {
        showSummary(documentId);
    }

    if (action === "summary-audio") {
        playSummaryAudio(documentId);
    }

    if (action === "paraphrase") {
        showParaphrase(documentId);
    }

    if (action === "audio") {
        playAudio(documentId);
    }

    if (action === "reprocess") {
        reprocessDocument(documentId);
    }

    if (action === "delete") {
        deleteDocument(documentId);
    }
});
// =========================
// REPROCESS DOCUMENT
// =========================

async function reprocessDocument(documentId) {

    const token = localStorage.getItem("access_token");

    if (!token) {
        return;
    }

    try {

        resultSection.classList.remove("hidden");

        resultTitle.textContent = "Reprocessing";
        resultContent.textContent =
            "Processing document. Please wait...";

        const response = await fetch(
            `/documents/${documentId}/process`,
            {
                method: "PUT",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Reprocessing failed"
            );
        }

        resultTitle.textContent = "Reprocessing Complete";

        resultContent.textContent =
            "Document reprocessed successfully.";

        await loadDocuments();

    } catch (error) {

        console.error(
            "Reprocess error:",
            error
        );

        resultTitle.textContent = "Reprocessing Error";

        resultContent.textContent =
            error.message;
    }
}
// =========================
// DELETE DOCUMENT
// =========================

async function deleteDocument(documentId) {

    const token = localStorage.getItem("access_token");

    if (!token) {
        return;
    }

    const confirmed = confirm(
        "Are you sure you want to delete this document?"
    );

    if (!confirmed) {
        return;
    }

    try {

        const response = await fetch(
            `/documents/${documentId}`,
            {
                method: "DELETE",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Delete failed"
            );
        }

        resultSection.classList.remove("hidden");

        resultTitle.textContent = "Document Deleted";

        resultContent.textContent =
            "Document deleted successfully.";

        await loadDocuments();

    } catch (error) {

        console.error(
            "Delete error:",
            error
        );

        resultTitle.textContent = "Delete Error";

        resultContent.textContent =
            error.message;
    }
}

// =========================
// PLAY SUMMARY AUDIO
// =========================

async function playSummaryAudio(documentId) {

    const token = localStorage.getItem("access_token");

    if (!token) {
        return;
    }

    resultSection.classList.remove("hidden");

    resultTitle.textContent = "Summary Audio";
    resultContent.textContent = "Loading summary audio...";

    try {

        const response = await fetch(
            `/documents/${documentId}/summary-audio`,
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        if (!response.ok) {
            const data = await response.json();

            throw new Error(
                data.detail || "Failed to load summary audio"
            );
        }

        const audioBlob = await response.blob();

        if (currentAudioUrl) {
            URL.revokeObjectURL(currentAudioUrl);
        }

        currentAudioUrl =
            URL.createObjectURL(audioBlob);

        const audioPlayer =
            document.createElement("audio");

        audioPlayer.controls = true;
        audioPlayer.src = currentAudioUrl;

        resultContent.innerHTML = "";

        resultContent.appendChild(audioPlayer);

    } catch (error) {

        console.error(
            "Summary audio error:",
            error
        );

        resultContent.textContent =
            `Error: ${error.message}`;
    }
}