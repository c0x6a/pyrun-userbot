#! /usr/bin/env python
"""
Telegram userbot that runs Python code.

Made using Telethon
"""

import logging
import os

from telethon import TelegramClient, events

from .utils import code_to_image, remove_files, run_code

logging.basicConfig(level=20)
logger = logging.getLogger("userbot")

api_id = 000000  # Your API ID
api_hash = "abcde1234"  # Your API Hash

client = TelegramClient("SESSION", api_id, api_hash).start()


@client.on(events.NewMessage(outgoing=True, pattern="!!py*"))
@client.on(events.MessageEdited(outgoing=True, pattern="!!py*"))
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

    code_result = await run_code(code_file, this_folder)

    argument = command.split()
    if len(argument) > 1 and argument[1] == "img":
        await code_to_image(chat, code_file, code_result, this_folder, client)
        await event.delete()
    else:
        source = '\n'.join(chunks)
        response_string = (f"**Python code:**\n```{source}```\n\n"
                           f"**Result:**\n```{code_result}```")
        await event.edit(response_string)
        remove_files([f"{this_folder}/{code_file}"])


logger.info("starting...")
client.start()
logger.info("started!")
client.run_until_disconnected()
