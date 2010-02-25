# -*- coding: utf-8 -*-
import sys, os

from PyQt4 import QtCore, QtGui

styleList= [
    'heading1',
    'heading2',
    'code',
    'normal',
    ]

formats={
    'heading1': {
        'bold': True,
        'italic': False,
        'alignment': 'center',
        'font': 'White Rabbit',
        'size': 18,
        'nextStyle': 'normal',
        },
    'heading2': {
        'bold': True,
        'italic': True,
        'alignment': 'center',
        'font': 'Eurofurence',
        'size': 16,
        'nextStyle': 'normal',
        },
    'code': {
        'bold': False,
        'italic': False,
        'alignment': 'left',
        'font': 'Courier',
        'size': 10,
        'nextStyle': 'code',
        },    
    'normal': {
        'bold': False,
        'italic': False,
        'alignment': 'left',
        'font': 'Helvetica',
        'size': 10,
        'nextStyle': 'normal',
        },    
}

alignments = {
    'center': QtCore.Qt.AlignCenter,
    'left':QtCore.Qt.AlignLeft,
    'right':QtCore.Qt.AlignRight
    }

bfDict={}

for format in formats:
    bfDict[format]=QtGui.QTextBlockFormat()
    bfDict[format].setAlignment(alignments[formats[format]['alignment']])
    

class blockStyler(QtGui.QSyntaxHighlighter):
    def highlightBlock(self, text):
        text=unicode(text)
        block=self.currentBlock()
        st=block.userState()
        format=formats['normal']
        stName='normal'
        if st == -1: # No style set
            pb=block.previous()
            if pb.isValid():
                # Get previous style
                st2=pb.userState()
                pname=styleList[st2]
                stName=formats[pname]['nextStyle']
                format=formats[stName]
                block.setUserState(styleList.index(stName))
        else:
            stName=styleList[st]
            format=formats[stName]
        print text,'=>', stName

        # Creat text format, again, should be pre-made
        tf=QtGui.QTextCharFormat()
        tf.setFontFamily(format['font'])
        tf.setFontPointSize(format['size'])
        tf.setFontItalic(format['italic'])
        tf.setFontWeight(format['bold'] and 75 or 50)
        
        cursor=QtGui.QTextCursor(self.document())
        cursor.setPosition(block.position())
        cursor.setBlockFormat(bfDict[stName])
        self.setFormat(0, len(text), tf)
        self.lock=False


class FunDocument(QtGui.QTextDocument):
    def toRst(self):
        out=[]
        doc=w.document()
        bl=doc.begin()
        lastStyle=None
        while True:
            text=unicode(bl.text())
            style=styleList[bl.userState()]
            if style=='heading1':
                text=text.strip()
                out.append('')
                out.append(text)
                out.append('='*len(text))
                out.append('')
            elif style=='heading2':
                text=text.strip()
                out.append('')
                out.append(text)
                out.append('-'*len(text))
                out.append('')
            elif style=='code':
                if lastStyle!='code':
                    out.append('')
                    out.append('::')
                    out.append('')
                text='    '+text
                out.append(text)
            else:
                text=text.strip()
                out.append(text)
            lastStyle=style
            bl=bl.next()
            if not bl.isValid():
                break
        return '\n'.join(out)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window=QtGui.QWidget()
    window.show()
        
    w = QtGui.QTextEdit()
    w.d=FunDocument()
    w.setDocument(w.d)
    process=QtGui.QPushButton("Do Something")
    styles=QtGui.QComboBox()
    for s in styleList:
        styles.addItem(s)


    layout=QtGui.QVBoxLayout()
    layout.addWidget(process)
    layout.addWidget(styles)
    layout.addWidget(w)

    window.setLayout(layout)

    bs=blockStyler(w.document())

    def changeStyle(idx):
        block=w.textCursor().block()
        block.setUserState(idx)
        bs.rehighlightBlock(block)
        w.setFocus()

    def adjustStyleCombo():
        block=w.textCursor().block()
        st=block.userState()
        if st== -1: st=len(styleList)-1
        styles.setCurrentIndex(st)
        
    def doProcess():
        rst=w.document().toRst()
        try:
            os.unlink('outfile')
        except:
            pass
        f=open ('outfile','w')
        f.write(rst)
        f.close()
        os.system('rst2pdf outfile')
        os.system('okular outfile.pdf')
        os.system('rst2html outfile outfile.html')
        os.system('arora outfile.html')
        
        open('savedfile.xx','w').write(unicode(w.toHtml()))
            
    process.clicked.connect(doProcess)
    w.cursorPositionChanged.connect(adjustStyleCombo)
    styles.activated.connect(changeStyle)
    
    if len(sys.argv) >1:
        if sys.argv[1].endswith('.xx'):
            w.setHtml(open(sys.argv[1]).read())
        else:
            w.setPlainText(open(sys.argv[1]).read())
        bs.rehighlight()

    sys.exit(app.exec_())
