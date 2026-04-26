# LMS-Discord-AI
### Simple Discord Bot for LM Studio | GUI with logs, status monitoring and easy management | Ability to send pictures
### LMS-Discord-AI is a powerful yet lightweight bridge between your local LM Studio server and Discord. It features a modern graphical interface (GUI) for real-time system monitoring and easy bot management.

## 🌟 Key Advantages
* **GUI Management**: A user-friendly CustomTkinter window with live logs and bot status.

* **Hardware Monitoring**: Built-in tracking of VRAM usage and GPU Temperature (perfect for keeping an eye on your hardware during inference).

* **Vision Support**: Analyze images and photos by using Vision-enabled models locally.

* **Identity Awareness**: The bot recognizes user nicknames and provides personalized interactions.

* **Plug & Play**: Automated dependency installation via a single .bat file—no manual terminal setup required.

## ⚙️ LM Studio Configuration
### To connect the bot to your AI model, follow these steps:

1. Open **LM Studio** and load your desired model.

2. Go to the **Local Server** tab (the ```<->``` icon).

3. In the right sidebar, ensure that:

  *   **Port** is set to ```1234``` (must match your config.json).

  *   **CORS** is toggled **ON**.

Click **Start Server**.

## 🧠 Adjusting Memory & Tokens
You can easily customize how the bot "thinks" and "remembers" inside the ```nebot.py``` file:

### 1. Context Memory (How much it remembers)
Locate this line in the ```process_ai_request``` function:

```Python
context = chat_histories[user_id][-5:]
```
* **Modification**: Change ```-5``` to any number (e.g., ```-10```). This determines how many previous messages the bot keeps in its "head."
* **Pro Tip**: For GPUs like the RTX 2060 Super, keeping this between 5 and 10 is ideal to prevent VRAM overflow.

## 2. Response Length & Creativity
Locate the API call section:

```Python
max_tokens=4096,
temperature=0.7
```
* **max_tokens**: Limits the length of the bot's response. Lower it to ```1024``` if you prefer shorter, snappier answers.

* **temperature**: Controls randomness. Use ```0.2``` for factual/strict answers or ```1.2``` for creative/chaotic ones.

## 🛠️ Quick Start
1. Rename ```config.example.json``` to ```config.json``` and paste your Discord Token.

2. Start the server in **LM Studio**.

3. Run ```run.bat``` — it will automatically handle library installations and launch the interface.
