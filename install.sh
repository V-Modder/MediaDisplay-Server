#!/bin/sh

cat << EOF
screen_width = Window.GetWidth();
screen_height = Window.GetHeight();

theme_image = Image("splash.png");
image_width = theme_image.GetWidth();
image_height = theme_image.GetHeight();

scale_x = image_width / screen_width;
scale_y = image_height / screen_height;

flag = 1;

if (scale_x > 1 || scale_y > 1)
{
        if (scale_x > scale_y)
        {
                resized_image = theme_image.Scale (screen_width, image_height / scale_x);
                image_x = 0;
                image_y = (screen_height - ((image_height  * screen_width) / image_width)) / 2;
        }
        else
        {
                resized_image = theme_image.Scale (image_width / scale_y, screen_height);
                image_x = (screen_width - ((image_width  * screen_height) / image_height)) / 2;
                image_y = 0;
        }
}
else
{
        resized_image = theme_image.Scale (image_width, image_height);
        image_x = (screen_width - image_width) / 2;
        image_y = (screen_height - image_height) / 2;
}

if (Plymouth.GetMode() != "shutdown")
{
        sprite = Sprite (resized_image);
        sprite.SetPosition (image_x, image_y, -100);
}

fun message_callback (text) {
        sprite.SetImage (resized_image);
}

Plymouth.SetUpdateStatusFunction(message_callback);

EOF > /usr/share/plymouth/themes/pix/pix.script
mv splash.png /usr/share/plymouth/themes/pix

disable_splash=1 > config.txt
# sed ?
splash quiet > cmdline.txt
#https://wiredzero.com/kiosk
#Disable the Raspberry Pi ‘color test’ by adding the line disable_splash=1 to /boot/config.txt.
#Disable the Raspberry Pi logo in the corner of the screen by adding logo.nologo to /boot/cmdline.txt.
#Disable the various bits of output from the kernel and friends by adding consoleblank=0 loglevel=1 quiet to /boot/cmdline.txt.

#Remove Taskbar
#Change background
#Disable screensaver
#Autostart app