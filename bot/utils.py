import subprocess


async def code_to_image(chat, code_file, code_result, this_folder, client):
    """Convert code to image using pygments and imagemagick."""
    output_file = "code_result.txt"
    image_file_code = "code_image.png"
    image_file_result = "code_result.png"

    await text_to_image(code_file, image_file_code, this_folder)
    await improve_image(image_file_code, this_folder)

    if code_result:
        image_output_complete = "final.png"
        with open(f"{this_folder}/{output_file}", "w") as f:
            f.writelines([
                "\nResult:\n",
                str(code_result),
            ])

        await text_to_image(output_file, image_file_result, this_folder)
        await improve_image(image_file_result, this_folder)

        subprocess.run([
            "convert",
            f"{this_folder}/{image_file_code}",
            f"{this_folder}/{image_file_result}",
            "-append",
            f"{this_folder}/{image_output_complete}",
        ])

        await client.send_file(
            chat,
            file=f"{this_folder}/{image_output_complete}",
        )

        remove_files([
            f"{this_folder}/{image_file_result}",
            f"{this_folder}/{output_file}",
            f"{this_folder}/{image_output_complete}",
        ])
    else:
        await client.send_file(
            chat,
            file=f"{this_folder}/{image_file_code}",
        )
    remove_files([
        f"{this_folder}/{code_file}",
        f"{this_folder}/{image_file_code}",
    ])


async def improve_image(image_file_code, folder):
    """Invert colors, resize if bigger than 700px width or extent to
    700px width using black background
    """
    subprocess.run([
        "convert",
        f"{folder}/{image_file_code}",
        "-negate",
        "-resize",
        "700x>",
        "-background",
        "black",
        "-extent",
        "700x",
        f"{folder}/{image_file_code}",
    ])


async def text_to_image(code_file, image_file, folder):
    """Convert text file to image using pygments."""
    subprocess.run([
        "pygmentize",
        "-o",
        f"{folder}/{image_file}",
        f"{folder}/{code_file}",
    ])


async def run_code(code_file, this_folder):
    """Run Python code"""
    return subprocess.run([
        "python",
        f"{this_folder}/{code_file}"
    ], capture_output=True).stdout.decode()


def remove_files(files_list):
    """Remove a list of files using ``rm`` command"""
    subprocess.run(["rm"] + files_list)
