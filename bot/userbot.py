#! /usr/bin/env python
"""
Telegram userbot that runs Python code.

Made using Telethon
"""

import logging
import os
import subprocess
from telethon import TelegramClient, events

logging.basicConfig(level=20)
logger = logging.getLogger("userbot")

api_id = 000000  # Your API ID
api_hash = "abcde1234"  # Your API Hash

client = TelegramClient("SESSION", api_id, api_hash).start()


@client.on(events.NewMessage(outgoing=True, pattern="!!py*"))
async def python_code_run(event):
    """Receive a message that contains a command (!!py) and Python code
    to run, example:

    ```
    !!py
    print("Hello World!")
    ```
    """
    chat = await event.get_input_chat()
    command_chunks = event.raw_text.split("\n")
    command, chunks = command_chunks[:1][0], command_chunks[1:]

    this_folder = os.path.dirname(os.path.realpath(__file__))
    code_file = "code.py"

    with open(f"{this_folder}/{code_file}", "w") as f_code:
        for chunk in chunks:
            f_code.write(f"{chunk}\n")

    code_result = subprocess.run([
        "python",
        f"{this_folder}/{code_file}"
    ], capture_output=True).stdout.decode()

    argument = command.split()
    if len(argument) > 1 and argument[1] == "img":
        await code_to_image(chat, code_file, code_result, this_folder)
    else:
        await event.reply(f"**Result:**\n```{code_result}```")
        subprocess.run([
            "rm",
            f"{this_folder}/{code_file}",
        ])


async def code_to_image(chat, code_file, code_result, this_folder):
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

        subprocess.run([
            "rm",
            f"{this_folder}/{image_file_result}",
            f"{this_folder}/{output_file}",
            f"{this_folder}/{image_output_complete}",
        ])
    else:
        await client.send_file(
            chat,
            file=f"{this_folder}/{image_file_code}",
        )
    subprocess.run([
        "rm",
        f"{this_folder}/{code_file}",
        f"{this_folder}/{image_file_code}",
    ])


async def improve_image(image_file_code, this_folder):
    """Invert colors, resize if bigger than 700px width or extent to
    700px width using black background
    """
    subprocess.run([
        "convert",
        f"{this_folder}/{image_file_code}",
        "-negate",
        "-resize",
        "700x>",
        "-background",
        "black",
        "-extent",
        "700x",
        f"{this_folder}/{image_file_code}",
    ])


async def text_to_image(code_file, image_file, folder):
    """Convert text file to image using pygments."""
    subprocess.run([
        "pygmentize",
        "-o",
        f"{folder}/{image_file}",
        f"{folder}/{code_file}",
    ])


logger.info("starting...")
client.start()
logger.info("started!")
client.run_until_disconnected()
