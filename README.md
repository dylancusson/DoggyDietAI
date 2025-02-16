# DoggyDietAI
![IMG_6483](https://github.com/user-attachments/assets/20d545dd-a92e-41dd-bda3-a7e78cd23f9b)
This is Lincoln, our Yorkie Terrier. While he may not look it (due to this old photo), Link has a bit of a weight problem.
Typically, you might just lower your dog's food intake and call it a day but two problems prevent us from doing just that:
1. Yorkies are prone to hypoglycemia so our vet recommended keeping food available 24/7.
2. Lincoln won't eat unless his bowl is mostly full.

This leads to family just topping off his bowl whenever it starts to look low, and with several people doing so it becomes quite
difficult to accurrately track just how much Link is eating.

Which makes for a perfect opportunity to put the Raspberry Pi camera to work!

DDAI counts the amount of kibble on startup, then waits for motion to be detected before rescanning and determining how many pieces were eaten.

The current version simply detects all motion but future versions will look for Link specifically to time his eating duration and total pieces.
Currently logging is done to a text file but this will likely change when I implement a dashboard and notifications.

