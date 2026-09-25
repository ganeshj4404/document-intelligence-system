from googleapiclient.errors import HttpError

from app.services.google_drive_service import get_drive_service


def main():
    print("===== GOOGLE DRIVE INTEGRATION TEST =====\n")

    try:
        # 1. Authenticate and create Drive service
        print("1. Authenticating with Google Drive...")
        service = get_drive_service()

        print("Authentication successful.\n")

        # 2. Get information about the authenticated user's Drive
        print("2. Checking Google Drive access...")

        about = (
            service.about()
            .get(fields="user(displayName,emailAddress)")
            .execute()
        )

        user = about["user"]

        print(f"Connected account: {user.get('displayName')}")
        print(f"Email: {user.get('emailAddress')}\n")

        # 3. List files from Google Drive
        print("3. Reading files from Google Drive...")

        response = (
            service.files()
            .list(
                pageSize=20,
                orderBy="modifiedTime desc",
                fields=(
                    "nextPageToken,"
                    "files(id,name,mimeType,size,modifiedTime)"
                )
            )
            .execute()
        )

        files = response.get("files", [])

        if not files:
            print("No files found in Google Drive.")
            return

        print(f"Found {len(files)} file(s).\n")

        # 4. Display file information
        print("===== DRIVE FILES =====\n")

        for index, file in enumerate(files, start=1):

            print(f"{index}. {file['name']}")
            print(f"   ID: {file['id']}")
            print(f"   Type: {file['mimeType']}")
            print(f"   Modified: {file.get('modifiedTime', 'N/A')}")
            print(f"   Size: {file.get('size', 'N/A')}")
            print()

        print("===== TEST PASSED =====")
        print("Google Drive authentication and file listing are working.")

    except HttpError as error:

        print("\nGoogle Drive API error:")
        print(error)

    except FileNotFoundError:

        print("\ncredentials.json was not found.")

        print(
            "Make sure it is located at:"
            "\ncredentials/credentials.json"
        )

    except Exception as error:

        print("\nUnexpected error:")
        print(error)


if __name__ == "__main__":
    main()