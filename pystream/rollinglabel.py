from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QTimer, QPoint, QPointF, QSize
from PyQt5.QtGui import QPainter, QImage, QStaticText, QTransform, qRgb, qRgba

# https://stackoverflow.com/questions/10651514/text-scrolling-marquee-in-qlabel

class RollingLabel(QLabel):
    def __init__(self, parent=None):
        super(RollingLabel, self).__init__(parent)
        self.timer=QTimer()
        self.timer.timeout.connect(self.updateR)
        self.timer.start(55)
        
        self.wholeTextSize = QSize(0,0)
        self.singleTextWidth = 0

        self.scrollEnabled = False
        self.scrollPos = 0


        self.buffer = QImage()
        self.alphaChannel = QImage()

        self.staticText = QStaticText("")
        self.staticText.setTextFormat(Qt.PlainText);

        self.setFixedHeight(self.fontMetrics().height());
        self.leftMargin = self.height() / 3;
        self._text = ""

    def text(self):
        return self._text;

    def setText(self, text):
        self._text = text;
        self.updateText();
        self.update();

    def paintEvent(self, event):
        p = QPainter(self)

        if self.scrollEnabled:
            self.buffer.fill(qRgba(0, 0, 0, 0));
            pb = QPainter(self.buffer);
            pb.setPen(p.pen());
            pb.setFont(p.font());

            x = min(-self.scrollPos, 0) + self.leftMargin;
            while x < self.width():
                pb.drawStaticText(QPointF(x, (self.height() - self.wholeTextSize.height()) / 2) + QPoint(2, 2), self.staticText)
                x += self.wholeTextSize.width()

            #Apply Alpha Channel
            pb.setCompositionMode(QPainter.CompositionMode_DestinationIn)
            pb.setClipRect(self.width() - 15, 0, 15, self.height());
            pb.drawImage(0, 0, self.alphaChannel);
            pb.setClipRect(0, 0, 15, self.height());
            #initial situation: don't apply alpha channel in the left half of the image at all; apply it more and more until scrollPos gets positive
            if self.scrollPos < 0:
                pb.setOpacity((max(-8, self.scrollPos) + 8) / 8.0)
            pb.drawImage(0, 0, self.alphaChannel)

            p.drawImage(0, 0, self.buffer)
        else:
            x = (self.width() - self.wholeTextSize.width()) / 2
            y = (self.height() - self.wholeTextSize.height()) / 2
            p.drawStaticText(QPointF(x, y), self.staticText)

    def updateR(self):
        self.scrollPos = (self.scrollPos + 2) % self.wholeTextSize.width();
        self.update()

    def updateText(self):
        self.timer.stop();

        self.singleTextWidth = self.fontMetrics().width(self._text);
        self.scrollEnabled = (self.singleTextWidth > self.width() - self.leftMargin);

        if self.scrollEnabled:
            self.scrollPos = -64
            self.staticText.setText(self._text)
            self.timer.start()
        else:
            self.staticText.setText(self._text)

        self.staticText.prepare(QTransform(), self.font());
        self.wholeTextSize = QSize(self.fontMetrics().width(self.staticText.text()), self.fontMetrics().height());

    def resizeEvent(self, event):
        #When the widget is resized, we need to update the alpha channel.
        self.alphaChannel = QImage(self.size(), QImage.Format_ARGB32_Premultiplied);
        self.buffer = QImage(self.size(), QImage.Format_ARGB32_Premultiplied);

        #Create Alpha Channel:
        if self.width() > 64:
            #create first scanline
            scanline = [0] * self.width()
            for x in range(0, 15):
                scanline[x] = scanline[self.width() - x - 1] = qRgba(0, 0, 0, x << 4)
            # Background
            for x in range(15, self.width() - 15):
                scanline[x] = qRgb(0, 0, 0)
            #copy scanline to the other ones
            for y in range(0, self.height()):
                for x in range(0, self.width()):
                    self.alphaChannel.setPixel(x, y, scanline[x])
        else:
            self.alphaChannel.fill(qRgba(0, 0, 0, 0))

        #Update scrolling state
        newScrollEnabled = (self.singleTextWidth > self.width() - self.leftMargin)
        if newScrollEnabled != self.scrollEnabled:
            self.updateText()