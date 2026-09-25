import mimetypes
from pathlib import Path


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload

# Allows the application to read and write files in Google Drive.
SCOPES = ["https://www.googleapis.com/auth/drive"]
SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".xlsx",
    ".xls",
    ".csv",
    ".pptx",
    ".png",
    ".jpg",
    ".jpeg",
}

# Project root:
# document-intelligence-system/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

CREDENTIALS_FILE = PROJECT_ROOT / "credentials" / "credentials.json"
TOKEN_FILE = PROJECT_ROOT / "credentials" / "token.json"


def get_drive_service():
    """
    Authenticate the user and return a Google Drive API service.
    """

    credentials = None

    # Reuse previously saved authentication token.
    if TOKEN_FILE.exists():
        credentials = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )

    # Authenticate if there is no valid token.
    if not credentials or not credentials.valid:

        if (
            credentials
            and credentials.expired
            and credentials.refresh_token
        ):
            credentials.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES
            )

            credentials = flow.run_local_server(
                port=0
            )

        # Save the token so we don't have to authorize every time.
        TOKEN_FILE.write_text(
            credentials.to_json(),
            encoding="utf-8"
        )

    # Create the Drive API service.
    service = build(
        "drive",
        "v3",
        credentials=credentials
    )

    return service


def download_drive_file(service, file_id, destination_path):
    """
    Download a regular binary file from Google Drive
    and save it to the specified local path.
    """

    destination_path = Path(destination_path)

    destination_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Get file metadata first.
    metadata = service.files().get(
        fileId=file_id,
        fields="id,name,mimeType,size,capabilities(canDownload)"
    ).execute()

    print(f"Drive file name: {metadata.get('name')}")
    print(f"Drive MIME type: {metadata.get('mimeType')}")
    print(f"Drive size: {metadata.get('size')} bytes")
    print(
        f"Can download: "
        f"{metadata.get('capabilities', {}).get('canDownload')}"
    )

    # Make sure the file is actually downloadable.
    if not metadata.get("capabilities", {}).get("canDownload", False):
        raise RuntimeError(
            "Google Drive reports that this file cannot be downloaded."
        )

    # Download the actual binary content.
    request = service.files().get_media(
        fileId=file_id
    )

    with open(destination_path, "wb") as file:

        downloader = MediaIoBaseDownload(
            file,
            request
        )

        done = False

        while not done:

            status, done = downloader.next_chunk()

            if status:
                progress = int(status.progress() * 100)
                print(f"Download progress: {progress}%")

    # Verify the local file size.
    local_size = destination_path.stat().st_size

    print(f"Local file size: {local_size} bytes")

    expected_size = metadata.get("size")

    if expected_size is not None:
        expected_size = int(expected_size)

        if local_size != expected_size:
            raise RuntimeError(
                f"Downloaded file size mismatch. "
                f"Expected {expected_size} bytes, "
                f"got {local_size} bytes."
            )

    print(f"File downloaded successfully to: {destination_path}")

    return destination_path

def export_google_doc(service, file_id, destination_path):
    """
    Export a Google Docs file as DOCX and save it locally.
    """

    destination_path = Path(destination_path)

    destination_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    request = service.files().export_media(
        fileId=file_id,
        mimeType="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    with open(destination_path, "wb") as file:

        downloader = MediaIoBaseDownload(
            file,
            request
        )

        done = False

        while not done:

            status, done = downloader.next_chunk()

            if status:
                progress = int(status.progress() * 100)
                print(f"Export progress: {progress}%")

    local_size = destination_path.stat().st_size

    print(
        f"Google Doc exported successfully to: "
        f"{destination_path}"
    )

    print(f"Local file size: {local_size} bytes")

    return destination_path

def get_all_descendant_folder_ids(service, root_folder_id):
    """
    Find the root folder and all subfolders inside it.
    This allows us to exclude the complete output folder tree.
    """

    folder_ids = {root_folder_id}
    folders_to_check = [root_folder_id]

    while folders_to_check:
        current_folder_id = folders_to_check.pop()

        query = (
            f"'{current_folder_id}' in parents "
            f"and mimeType = 'application/vnd.google-apps.folder' "
            f"and trashed = false"
        )

        response = service.files().list(
            q=query,
            fields="files(id,name)"
        ).execute()

        for folder in response.get("files", []):
            folder_id = folder["id"]

            if folder_id not in folder_ids:
                folder_ids.add(folder_id)
                folders_to_check.append(folder_id)

    return folder_ids

def list_supported_files(service, page_size=100, exclude_folder_id=None):
    """
    Find supported source documents while excluding the entire
    output folder and all of its subfolders.
    """

    excluded_folder_ids = set()

    if exclude_folder_id:
        excluded_folder_ids = get_all_descendant_folder_ids(
            service,
            exclude_folder_id
        )

    response = service.files().list(
        q="trashed = false",
        pageSize=page_size,
        fields="files(id,name,mimeType,size,parents,webViewLink)"
    ).execute()

    files = []

    for file in response.get("files", []):

        # Ignore folders
        if file.get("mimeType") == "application/vnd.google-apps.folder":
            continue

        # Ignore files located anywhere inside the output folder tree
        parents = file.get("parents", [])

        if any(parent_id in excluded_folder_ids for parent_id in parents):
            continue

        name = file.get("name", "")
        mime_type = file.get("mimeType", "")

        supported = (
            Path(name).suffix.lower() in SUPPORTED_EXTENSIONS
            or mime_type in {
                "application/vnd.google-apps.document",
                "application/vnd.google-apps.spreadsheet",
                "application/vnd.google-apps.presentation",
            }
        )

        if supported:
            files.append(file)

    return files


def export_google_workspace_file(
    service,
    file_id,
    destination_path,
    export_mime_type
):
    """
    Export a Google Workspace file into a local file.
    """

    destination_path = Path(destination_path)

    destination_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    request = service.files().export_media(
        fileId=file_id,
        mimeType=export_mime_type
    )

    with open(destination_path, "wb") as file:

        downloader = MediaIoBaseDownload(
            file,
            request
        )

        done = False

        while not done:

            status, done = downloader.next_chunk()

            if status:
                progress = int(status.progress() * 100)
                print(f"Export progress: {progress}%")

    local_size = destination_path.stat().st_size

    print(
        f"Workspace file exported successfully to: "
        f"{destination_path}"
    )

    print(f"Local file size: {local_size} bytes")

    return destination_path

def process_drive_file(
    service,
    file_id,
    file_name,
    mime_type,
    destination_directory="data/input"
):
    """
    Download a normal Drive file or export a Google Workspace file.
    Returns the local file path.
    """

    destination_directory = Path(destination_directory)
    destination_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    # Google Docs → DOCX
    if mime_type == "application/vnd.google-apps.document":

        output_path = (
            destination_directory
            / f"{file_name}.docx"
        )

        return export_google_doc(
            service,
            file_id,
            output_path
        )

    # Google Sheets → XLSX
    elif mime_type == "application/vnd.google-apps.spreadsheet":

        output_path = (
            destination_directory
            / f"{file_name}.xlsx"
        )

        return export_google_workspace_file(
            service,
            file_id,
            output_path,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Google Slides → PPTX
    elif mime_type == "application/vnd.google-apps.presentation":

        output_path = (
            destination_directory
            / f"{file_name}.pptx"
        )

        return export_google_workspace_file(
            service,
            file_id,
            output_path,
            "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )

    # Normal uploaded files → download
    else:

        output_path = (
            destination_directory
            / file_name
        )

        return download_drive_file(
            service,
            file_id,
            output_path
        )

def get_or_create_output_folder(
    service,
    folder_name="Document Intelligence Outputs"
):
    """
    Find the output folder in Google Drive.
    Create it if it does not exist.
    """

    query = (
        f"name = '{folder_name}' "
        "and mimeType = 'application/vnd.google-apps.folder' "
        "and trashed = false"
    )

    response = service.files().list(
        q=query,
        spaces="drive",
        fields="files(id,name)"
    ).execute()

    folders = response.get("files", [])

    if folders:
        return folders[0]["id"]

    folder_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder"
    }

    folder = service.files().create(
        body=folder_metadata,
        fields="id,name"
    ).execute()

    print(
        f"Created Drive output folder: "
        f"{folder['name']}"
    )

    return folder["id"]

def get_or_create_subfolder(
    service,
    parent_folder_id,
    folder_name
):
    """
    Find or create a subfolder inside a parent Drive folder.
    """

    query = (
        f"name = '{folder_name}' "
        "and mimeType = 'application/vnd.google-apps.folder' "
        f"and '{parent_folder_id}' in parents "
        "and trashed = false"
    )

    response = service.files().list(
        q=query,
        spaces="drive",
        fields="files(id,name)"
    ).execute()

    folders = response.get("files", [])

    if folders:
        return folders[0]["id"]

    folder_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_folder_id]
    }

    folder = service.files().create(
        body=folder_metadata,
        fields="id,name"
    ).execute()

    print(
        f"Created Drive subfolder: "
        f"{folder['name']}"
    )

    return folder["id"]


def upload_file_to_drive(
    service,
    local_file_path,
    folder_id
):
    """
    Upload a local file to a Google Drive folder.
    """

    local_file_path = Path(local_file_path)

    if not local_file_path.exists():
        raise FileNotFoundError(
            f"File not found: {local_file_path}"
        )

    mime_type = (
        mimetypes.guess_type(
            local_file_path.name
        )[0]
        or "application/octet-stream"
    )

    file_metadata = {
        "name": local_file_path.name,
        "parents": [folder_id]
    }

    media = MediaFileUpload(
        str(local_file_path),
        mimetype=mime_type,
        resumable=True
    )

    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id,name,mimeType,size,webViewLink"
    ).execute()

    return uploaded_file

def delete_existing_file(service, folder_id, file_name):
    query = (
        f"'{folder_id}' in parents "
        f"and name = '{file_name}' "
        f"and trashed = false"
    )

    response = service.files().list(
        q=query,
        fields="files(id,name)"
    ).execute()

    existing_files = response.get("files", [])

    for file in existing_files:
        service.files().delete(
            fileId=file["id"]
        ).execute()

        print(f"Replaced existing file: {file['name']}")