# -*- coding: utf-8 -*-
import sys, os

from PyQt4 import QtCore, QtGui

from pythonutils.odict import OrderedDict
styles=OrderedDict([
    ('heading1', {
        'bold': True,
        'italic': False,
        'alignment': 'center',
        'font': 'White Rabbit',
        'size': 18,
        'nextStyle': 'normal',
        }),
    ('heading2', {
        'bold': True,
        'italic': True,
        'alignment': 'center',
        'font': 'Eurofurence',
        'size': 16,
        'nextStyle': 'normal',
        }),
    ('code', {
        'bold': False,
        'italic': False,
        'alignment': 'left',
        'font': 'Courier',
        'size': 10,
        'nextStyle': 'code',
        }),    
    ('normal', {
        'bold': False,
        'italic': False,
        'alignment': 'left',
        'font': 'Helvetica',
        'size': 10,
        'nextStyle': 'normal',
        })])


alignments = {
    'center': QtCore.Qt.AlignCenter,
    'left':QtCore.Qt.AlignLeft,
    'right':QtCore.Qt.AlignRight
    }



class StyleData(QtGui.QTextBlockUserData):
    def __init__(self, data='normal'):
        self.data=data
        QtGui.QTextBlockUserData.__init__(self)

class blockStyler(QtGui.QSyntaxHighlighter):
    def highlightBlock(self, text):
        text=unicode(text)
        stName='normal'
        format=styles['normal']
        block=self.currentBlock()
        st=block.userData()
        if not st: # No style set
            pb=block.previous()
            if pb.isValid():
                # Get previous style
                if pb and pb.userData():
                    prevStyle=pb.userData().data
                else:
                    prevStyle='normal'
                stName=styles[prevStyle]['nextStyle']
                format=styles[stName]
                block.setUserData(StyleData(stName))
        else:
            stName=st.data
            format=styles[stName]

        # Creat text format, again, should be pre-made
        tf=QtGui.QTextCharFormat()
        tf.setFontFamily(format['font'])
        tf.setFontPointSize(format['size'])
        tf.setFontItalic(format['italic'])
        tf.setFontWeight(format['bold'] and 75 or 50)
        
        self.updateBlockFormat(block, stName)
        self.setFormat(0, len(text), tf)
        self.lock=False

    def updateBlockFormat(self, block, stName=None):
        '''given a block and a style name, updates
        the block's style according to style[stName].
        
        if stName is None, use the block's stName 
        and if that is not there, use 'normal'
        '''
        
        if stName is None:
            if block.userData() and block.userData().data:
                stName=block.userData().data
            else:
                stName='normal'
        
        cursor=QtGui.QTextCursor(self.document())
        cursor.setPosition(block.position())
        current=cursor.blockFormat()
        # FIXME this will be much more extensive ;-)
        current.setAlignment(alignments[styles[stName]['alignment']])
        cursor.setBlockFormat(current)

class FunDocument(QtGui.QTextDocument):
    
    def indentText(self,text,indent):
        return '\n'.join((' '*indent)+l for l in text.splitlines())
    
    def toRst(self):
        out=[]
        doc=w.document()
        bl=doc.begin()
        lastStyle=None
        while True:
            text=unicode(bl.text())
            l=bl.textList()
            if l: # This is in a list
                text=self.indentText(text,5*l.format().indent())
                text='*'+text[1:]
            d=bl.userData()
            if d: 
                d=d.data
            else:
                d='normal'
            style=styles[d]
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
    stylesCombo=QtGui.QComboBox()
    for s in styles.keys():
        stylesCombo.addItem(s)

    bbar=QtGui.QHBoxLayout()
    b1=QtGui.QPushButton("bullet >")
    b2=QtGui.QPushButton("number >")
    b3=QtGui.QPushButton("<")
    b4=QtGui.QPushButton("4")
    b5=QtGui.QPushButton("5")
    b6=QtGui.QPushButton("6")
    bbar.addWidget(b1)
    bbar.addWidget(b2)
    bbar.addWidget(b3)
    bbar.addWidget(b4)
    bbar.addWidget(b5)
    bbar.addWidget(b6)

    layout=QtGui.QVBoxLayout()
    layout.addWidget(process)
    layout.addWidget(stylesCombo)
    layout.addLayout(bbar)
    layout.addWidget(w)

    window.setLayout(layout)

    bs=blockStyler(w.document())

    def changeStyle(idx):
        block=w.textCursor().block()
        s=StyleData(styles.keys()[idx])
        block.setUserData(s)
        bs.rehighlightBlock(block)
        w.setFocus()

    def adjustStylesCombo():
        block=w.textCursor().block()
        st=block.userState()
        if st== -1: st=len(styles)-1
        stylesCombo.setCurrentIndex(st)
        
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

    def listIn(kind):
        cursor=w.textCursor()
        block=cursor.block()
        # Is it a bullet already?
        l=block.textList()
        lformat=QtGui.QTextListFormat()
        bformat=cursor.blockFormat()
        if l:
            # Only can indent if it has the same indent as the previous one
            pl=block.previous().textList()
            if not pl:
                maxI=1
            else:
                maxI=pl.format().indent()+1
            lformat=l.format()
            lformat.setIndent(min(maxI,lformat.indent()+1))
        lformat.setStyle(kind)
        l=cursor.createList(lformat)
        w.setFocus()

    def bulletIn():
        listIn(QtGui.QTextListFormat.ListDisc)

    def numberIn():
        listIn(QtGui.QTextListFormat.ListDecimal)

    def listOut():
        cursor=w.textCursor()
        block=cursor.block()
        # Is it a bullet already?
        l=block.textList()
        lformat=QtGui.QTextListFormat()
        bformat=cursor.blockFormat()
        
        def cleanBlockFormat(block):
            l.remove(block)
            cursor.setBlockFormat(QtGui.QTextBlockFormat())
            bs.updateBlockFormat(block)
            
        
        if l:
            if l.format().indent()==1:
                # No previous list to join
                cleanBlockFormat(block)
            else:
                # This is a nested list, find the next outer
                pb=block
                while True:
                    pb=pb.previous()
                    if not pb:
                        cleanBlockFormat(block)
                        print 'Got to first block: break'
                        break
                    print 'Previous',pb.text()
                    pl=pb.textList()
                    if not pl:
                        print "This shouldn't happen"
                        cleanBlockFormat(block)
                        break
                    pi=pl.format().indent()
                    print 'INDENT:',pi,l.format().indent()
                    if pi==l.format().indent()-1:
                        pl.add(block)
                        break
        else:
            print "nothing to do"
        w.setFocus()

    process.clicked.connect(doProcess)
    w.cursorPositionChanged.connect(adjustStylesCombo)
    stylesCombo.activated.connect(changeStyle)
    b1.clicked.connect(bulletIn)
    b2.clicked.connect(numberIn)
    b3.clicked.connect(listOut)
    
    if len(sys.argv) >1:
        if sys.argv[1].endswith('.xx'):
            w.setHtml(open(sys.argv[1]).read())
        else:
            w.setPlainText(open(sys.argv[1]).read())
        bs.rehighlight()
    adjustStylesCombo()
    window.activateWindow()
    window.setFocus()
    w.setFocus()
    sys.exit(app.exec_())
