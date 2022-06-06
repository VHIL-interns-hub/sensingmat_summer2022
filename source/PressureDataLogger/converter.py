from io import BytesIO as StringIO
from string import Template
import base64

__version__ = "1.0"
renderers = []

try:
    import cv2
    import numpy

    def render_opencv(img, fmt="png"):
        if not isinstance(img, numpy.ndarray):
            return None

        retval, buf = cv2.imencode(".%s" % fmt, img)
        if not retval:
            return None

        return buf, "image/%s" % fmt

    renderers.append(render_opencv)
except ImportError:
    pass

try:
    from PIL import Image

    def render_pil(img, fmt="png"):
        if not callable(getattr(img, "save", None)):
            return None

        output = StringIO()
        img.save(output, format=fmt)
        contents = output.getvalue()
        output.close()

        return contents, "image/%s" % fmt

    renderers.append(render_pil)
except ImportError:
    pass

try:
    import pylab

    def render_pylab(img, fmt="png"):
        if not callable(getattr(img, "savefig", None)):
            return None

        output = StringIO()
        img.savefig(output, format=fmt)
        contents = output.getvalue()
        output.close()

        return contents, "image/%s" % fmt

    renderers.append(render_pylab)
except ImportError:
    pass


class VisualRecord(object):
    def __init__(self, title="", imgs=None, footnotes="", fmt="png"):
        self.title = title
        self.fmt = fmt

        if imgs is None:
            imgs = []

        self.imgs = imgs

        if not isinstance(imgs, (list, tuple, set, frozenset)):
            self.imgs = [self.imgs]

        self.footnotes = footnotes

    def render_images(self):
        rendered = []

        for img in self.imgs:
            for renderer in renderers:
                # Trying renderers we have one by one
                res = renderer(img, self.fmt)

                if res is None:
                    continue
                else:
                    rendered.append(res)
                    break

        return "".join(
            Template("""
                <figure style="display: inline-block;">
                <img src="data:$mime;base64,$data"/>
                <figcaption contenteditable="true" style="text-align: center; font-size: 24px">
                label
                </figcaption>
                </figure>""").substitute({
                "data": base64.b64encode(data).decode(),
                "mime": mime
            }) for data, mime in rendered)

    def render_footnotes(self):
        if not self.footnotes:
            return ""

        return Template("<pre>$footnotes</pre>").substitute({
            "footnotes": self.footnotes
        })

    def __str__(self):
        t = Template(
            """
            <details>
            <summary style="font-size: 24px;">$title <img src=$img alt="" style="height: 1em; float:right;" onerror="this.style.display='none'"/></summary>
            $imgs
            $footnotes
            </details>
            <hr/>""")

        imgs = self.render_images()
        if len(imgs)>3:
            img = ""
        else:
            img = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAALiQAAC4kBN8nLrQAAIABJREFUeJzt3XuYnWV97//P916TSUiGYzgIEa0NsEHqWbG61fTnMXYDWsnIzFoTBui+IioUEWtbdTeltfa3pSAeWiC2aJpZaxJnVFSsqUoFReVHYSNbQcWgCArGAAnkQLLWrPv7+yMTScIkmcN6nnsd3q/r4soc1nqeD7kuuD/rvp/nfkwAmpovWtTlxx57tKRjVCgcJffDZXaYYjxMZjv/cT9UZgfL/SCZzZX7XEkHSZorszly75JUkFSQWeF3X+9Ul1SXe/13X5uNyX27pG2SnpTZNrlvk9mTct8ss8flvknumxTCzj/NNqpe3yBpvT388G/t5pvH8v67AjB5ljoA0Mm8v/9Idz9ehcLxcj9eZs+S+/GSjpV0jKSjZXaEtdh/qy653B+TtF5m6yU9bNKD7v6gzB409we8UHgwrFr1aOqsQKdqqf+pAK3Gly8Pft99z5Z0gur1ExTCQkknSDpB7s8xs7mJIybl7tsk/VzSOpndJ/d1Jq1Tvb5OJ5/8gF12WUydEWhXFACgAXz58uD33rvQCoVT3f1USc/Vzj//m5nNSZ2vFbn0pKSfSrpb0j1yv1vu99hJJ91HMQBmjgIATJEPDs7xsbHnmfuLXHqxzF4k6Xm2c80dGRufNfi/MrtT7neqULhTGzb8MKxduyN1NqCVUACA/fDly4P/7GenSvpDmb1c0mmSTjGpK3E07MalMUk/lnSbpFtldqstXHgPMwXAvlEAgN3EUukQxfgqhfAqSX8o95ea2cGpc2Hq3H2zpP+SdKukWzRnzi3huus2J44FNA0KADpaXLp0vrm/2mNcJOk1MnuBPXV7HNqIS3WTfuDSt+V+s6rV74TR0cdS5wJSoQCgo8QlSw7S7NmvlvQGub9BZs9vtVvs0BguuaS7JH3d3L+hWbNusZUrt6fOBeSF//Gh7cW+vucrhMUye4PcX8VV+ZiIS0/K/RaZfUNmXwtDQz9KnQnIEgUAbccHB+d4tfpahXC63P+HmT0rdSa0Hpd+KekGmd2gRx75FncZoN1QANAW4tKl8xXjW+T+FkmvM7N5qTOhfbj7Vpl909yv92r1y1w7gHZAAUDL8sHBZ3i1+icyO0tmi7g1D3lwaUzu35LZ52X2xTA09NvUmYDpoACgpcSBgaMlvV0xvl3SfzezkDoTOpe7R5ndImmNduwYCaOjG1JnAiaLAoCmF88//2Dt2PE2uRdl9jpu00MzGp8Z+KakitVqX7SRkS2pMwH7QwFAU/Le3oLPmvVmMzvHpdPZZhetZHy74hvkvtLGxv7DRkbqqTMBe6MAoKnEpUtPUb1+nqSlZvaM1HmAmXLpIZNWeQjXhVWr7k2dB9iFAoDk4vnnH2zbt/e7dL7t3G8faEvu/j2Zfcaq1dUsESA1CgCSiX19z1eh8E5JAyb1pM4D5MXdn5A0pBCuZsMhpEIBQK7i4sWzNX9+r9zfaWavTJ0HSM2lWxTjNdq4cZTNhpAnCgByEfv6jlMI75bZMpOOTJ0HaDYubZB0raR/DuXyw6nzoP1RAJCpWCq9TNJ75N5rZrNS5wGanUtVuX/OpKusUrkjdR60LwoAGs6XLw++bt3bJL3XpFekzgO0Kpe+K/cr7cQTr7fLLoup86C9UADQMHHx4tl2xBGDbvY+k05MnQdoF+7+U0mXW622ykZGqqnzoD1QADBjsVQ6RDG+U2bv4d59IDsuPST3j2nOnGvDdddtTp0HrY0CgGmLS5Ycoe7u95rZhZIOTZ0H6BTuvknSJ036mFUqG1PnQWuiAGDKxh+9e6ncLzSzg1PnATqVuz8hs0+Y+5UUAUwVBQCT5v39R7rZpTK7kI17gOYxvrHQJ1WtXhlGRx9LnQetgQKAA4ql0iFyf5/MLmHgB5rX+IzAFVatXslWwzgQCgD2yQcH53itdqGkvzSz+anzAJic8U2FPqJHH72a3QWxLxQAPI0vWtTlCxacJ+mvzeyZqfMAmB53f0DS31qt9lkeSYy9UQCwh1gsni7po2Z2SuosABrDpbvl/uehUvla6ixoHhQASJK8WHyhS1eY2WtTZwGQDXf/hqRLQ6Xyw9RZkB4FoMPFvr7jVCj8vdzPMbOQOg+AbLl7lNlnrKvrQ7Zy5W9S50E6FIAO5b293T5r1qWSPmhm81LnAZAvd98ss7+zefOushUraqnzIH8UgA4U+/v/WCFcxX79AFz6iaSLQ7n89dRZkC8KQAeJZ5+9UF1dV5l0euosAJqLu19v9foltmbN/amzIB8UgA7gvb3d3t39l5I+YNLs1HkANCeXnpT0YZs373KWBdofBaDNxf7+RQrhGpNOTp0FQGsYv23wHaFS+W7qLMgOBaBNjT+w5x9NOjd1FgCtxyWX9C/m/hc8aKg9UQDaUCwWizL7uElHps4CoLW5tN7cL7JKZSR1FjQWBaCNxFLpWLlfY2Znps4CoL24++cV47vD6tXrU2dBY7DxS5vwYvFcud/D4A8gC2Z2lkK4O5ZKA6mzoDGYAWhx8ZxzFqhe/7RJb06dBUBncOkGSctCufxw6iyYPmYAWlgslfpVr/+QwR9Ansb3EvmRF4u9qbNg+pgBaEFeLB7uZlebdHbqLAA6m0tl6+q60Fau3JQ6C6aGAtBiYn//mxTCdSYdlzoLAEiSu/9KZueGcvnG1FkweRSAFhEXL56t+fM/atKfpc4CAHsb3zfgSqtWP2AjI9XUeXBgFIAWEEul/yZptUkvTJ0FAA7gDjfrC0ND61IHwf5xEWCTiwMD58n9DgZ/AC3iJYrx/3C7YPNjBqBJxfPPP1jbt19rZv2pswDAdLi0yqrVd9nIyJbUWfB0FIAmFPv6nq9CYdSkE1NnAYCZcOknks4K5fI9qbNgTywBNJlYKg2qULiVwR9AOzDpZLnfFvv7S6mzYE/MADQJHxyc42NjnzLpT1NnAYAsuHSNHn30PWHt2h2ps4AC0BTiwMBz5P4FLvQD0AHucPezQqXyy9RBOh1LAIl5sfh6ud/O4A+gQ7xEZrd7qfRHqYN0OgpAQrFYvNTN1pp0ROosAJAXk4506RuxWGRjs4RYAkjABwfneK32aTPjPlkAHc2lz+rRRy/guoD8UQByFs85Z4HV61+S9JLUWQCgGbh0m6S38njhfFEAchRLpRdL+goP8gGAPbn0oMzOCENDd6XO0im4BiAnsVT6E7l/h8EfAJ7OpOPlfkvs7z8jdZZOQQHIQezv/wtJnzezuamzAECzMqlHZtfHUum9qbN0ApYAMuSLFnX5ggXXmtn5qbMAQCtx92utVnu3jYzUU2dpVxSAjHhvb4/PmjViZotTZwGAVuTSDTZv3tm2YsW21FnaEQUgA7Gv7xgrFL4qrvQHgBlx6Tbt2HF6GB3dkDpLu6EANFhcuvQk1etrzew5qbMAQDtw93Wq1xeHNWvuS52lnVAAGij295+mEL5q0pGpswBAO3Fpg0L447Bq1e2ps7QL7gJokFgqvU4h3MjgDwCNZ9JRqtf/k2cINA4FoAFiqfQnkr5qUk/qLADQrszsYHf/WiyVzkydpR1QAGYoDgycJ2nEpNmpswBAuzOzOZI+H4vFpamztDoKwAzEYvESuf+rSYXUWQCgU5jUJbOVsVS6KHWWVkYBmKZYLP6VmV1pXEgJALkzyUz6RCwW35c6S6uiAExDLBaXm9lHUucAgE5nZpfHUumDqXO0Ij69TlEslf7OpA+lzgEAeIq7/22oVJanztFKKABTEEul/23S+1PnAAA8nUv/EMrlD6TO0SooAJPE4A8AzY8SMHlcAzAJsVj8MIM/ADQ/k/7KS6W/SZ2jFTADcACxVPprky5LnQMAMHkufSiUy3+fOkczowDsx/itflztDwAtyKX3h3L58tQ5mhUFYB9isXiJmV2ZOgcAYPpc+rNQLn8ydY5mRAGYQBwYOG98hz/+fgCghbnkks4J5fJQ6izNhgFuL7FYfJvMPsf2vgDQHlwak3RWKJe/nDpLM6EA7MaLxde72Q082AcA2ou7bzezN1u5fFPqLM2CAjAuDgy8XO7f5JG+ANCe3H2zCoXXhlWrbk+dpRlQACTFpUtPUr3+PTObnzoLACA7Lm3Q2Ngrwpo196XOklrHbwQU+/qOUb2+lsEfANqfSUepUFgblyw5KnWW1Dq6AHhvb48VCl81s+ekzgIAyIeZnaDZs2/wZcvmps6SUscWAF+0qMtnzRqR9JLUWQAA+TLpNN+6dY339nbsHV+dWwAWLLjWzBanzgEASMOk0727+1Opc6TSkQUg9vf/hZmdnzoHACAtky6IxeIlqXOk0HF3AcRS6U8kfZ5d/gAAkuTuUdJbQqVyQ+oseeqoQTCWSi+W+3fMrKMv/AAA7MmlLTJ7VRgauit1lrx0TAGI55yzQPX6bSYdlzoLAKD5uPSgdXWdZitX/iZ1ljx0xDUAccmSg6xe/xKDPwBgX0w63mu16+PixR2xHXxHFAB1d68Qt/sBAA7AzF6uI464OnWOPLR9AYil0nvNbCB1DgBAazCz82KpdFHqHFlr62sAxp/ut5ZH+wIApsKlMcX4+jA8fHPqLFlp2wIQBwaeI/fbTToidRYAQOtxaYOF8FJbteqB1Fmy0JZLAD44OEfuX2DwBwBMl0lHeb3+ee/t7U6dJQvtWQDGxj5l0gtT5wAAtDYze6l3d1+VOkcW2m4JwIvFc2X2mdQ5AADtw91LoVKppM7RSG1VAGJf3/NVKNxq0kGpswAA2oe7b5XZaaFcvid1lkZpmwIQS6VDJN1u0ompswAA2o9LP7Fq9WU2MrIldZZGaJ9rANyvYfAHAGTFpJM1a1bbPD64LQpAHBg4z8z6U+cAALQ5s8HY319KHaMRWn4JwPv7T3az281sXuosAID25+6bFcKLw9DQutRZZqKlZwDi4sWzPYRhBn8AQF7M7GDFOOzLls1KnWUmWroAaP78j3K/PwAgb2b2Ut+69SOpc8xEyy4BxFLpjZLWWgv/OwAAWpdLLrPXh6Gh/0ydZTpacvCMS5Ycodmzf2jScamzAAA6l0sPWrX6PBsZeTx1lqlqzSWA2bP/mcEfAJCaScd7i94a2HIzALFU6jeprbZjBAC0Npd6Q7k8mjrHVLRUAYjnnLNA9foPTTo8dRYAAHZx90dl9rxQLj+cOstktdYSQL3+aQZ/AECzMbP5cr8mdY6paJkCEEulQZPenDoHAAATMbMzY7FYTJ1jslpiCSCWSsdKuptP/wCAZubujyqE54ahod+mznIgrTEDsPNBPwz+AICmZmbzFeM/pc4xGU1fAGKxWDSzM1PnAABgMsxsSRwYOCt1jgNp6iWAuHTpfMX4E5OOTJ0FAIDJcmm9dXWdbCtXbkqdZV+aewagXr+cwR8A0GpMOsbHxv4hdY79adoZgNjfv8hCuCl1DgAApsMll/TKUC7fmjrLRJpyBsB7e7sVQkvdTwkAwO7GH1a3whct6kqdZSLNWQC6u//SpJNT5wAAYCZMep4fd9ylqXNMpOmWAOLZZy9UV9fdJs1OnQUAgJly921WKJxiq1Y9kDrL7ppvBqCr62MM/gCAdmFmc71evyJ1jr011QxA7O//Ywvhq6lzAADQaC69PpTLN6bOsUvTzACMX/h3VeocAABkwv0TzXRBYNMUAHV3v9ekE1PHAAAgC2b2XF+w4KLUOXZpiiWA2Nd3nEK418zmpc4CAEBW3P0JxXhSWL16feoszTEDUCj8PYM/AKDdmdkhCuGy1DmkJpgB8GLxhS7dYWbNUUYAAMiQS3XV6y8Iq1ffnTJH8kHXpSsY/AEAncKkgkL4x9Q5kg68sVg83cxemzIDAAB5M7PFsVR6Y8oMyQqAL1rUJbPLU50fAICk3K/w3t5CqtOnKwALFpzHfv8AgE5lZn+gWbOWJjt/ipP64OAcr9XWmdmCFOcHAKAZuPRLq1ZPspGRat7nTjID4LXauxn8AQCdzqRn+6xZFyQ6d75iqXSI3H9uZvPzPjcAAM3G3X9rtdpCGxnZkud5858BcL+UwR8AgJ3M7GifNes9uZ83z5N5f/+RHsIvTOrJ87wAADQzd3/CpN+zSmVjXufMdQbAzS5l8AcAYE9mdohLl+R6zrxOFJcuna8Y76cAAAAwocfV1fV7tnLlpjxOlt8MQIx8+gcAYN8O9Vott1mAXGYA4pIlR6i7+34zOziP8wEA0KJymwXIZwagu/u9DP4AABzQoV6rXZzHiTKfAYil0iEmPSDp0KzPBQBAq3Npo1Wrz8p6X4DsZwBifKcY/AEAmBSTDvfu7mU5nCc7cfHi2TriiPvN7BlZngcAgHbi7r+ynp7ftxUralmdI9MZADviiEEGfwAApsbMnunbtg1keY7MCoAvXx7c7H1ZHR8AgLbm/n7PcKY+uwKwbt3bTDoxq+MDANDOTDrZi8Uzszp+dksA7rluaQgAQNsxe29mh87ioLFUeplJt2VxbAAAOonX6y8Oq1ff2ejjZjUDkPtjDQEAaEshZDKmNnwGIPb1HacQ7jezWY0+NgAAncalqur1Z4XVq9c38riNnwEI4d0M/gAANIZJ3QrhXRkct3Hi4sWzNX/+r0w6spHHBQCgk7n7b61WO95GRqqNOmZjZwDmz+9l8AcAoLHM7Gjv7j6rkcdsbAFwf2dDjwcAAHa5oJEHa9gSQOzre74VCnc16ngAAGBPLp0ayuV7GnGsxs0AFAp8+gcAIEvuDZsFaMgMQDz//IO1Y8dDJvU04ngAAGBCj2vevONsxYptMz1QQ2YAbPv2fgZ/AAAyd6i2bHl7Iw7UkALg0nmNOA4AANg/N2vImDvjJYC4dOkpFmNDLkgAAAAH5mYnhqGhdTM5xsxnAOp1Pv0DAJCnGM+d6SFmVAB80aIuSUtnGgIAAEzJoC9fPqMxfGYFYMGCxWb2jJkcAwAATI2ZPdPvvfcNMznGjAqAmZ0zk/cDAIBpCmFGM/DTvghw/N7/9SYdNJMAAABg6lzaYvPmHTPdPQGmPwOwY8fbGPwBAEjDpB7fuvUt033/9AuAe3Ha7wUAAI0w7bF4WksAcWDgaLk/ZFJhuicGAAAz4+41VavPCKOjj031vdOdAXg7gz8AAGmZ2SzNnt07nfdOrwDE2JB9iAEAwAy5T2tMnvISQOzrO0YhPGRmjXuUMAAAmBaX6hbjM2x4+JGpvG/qg7jZ2xj8AQBoDiYV3GzKdwNMpwCcNeX3AACA7ExjbJ7SEkBcunS+YvyNSV1TPREAAMiGS1Xr6jrGVq7cNNn3TG0GIMa3MPgDANBcTOr2Wu2MqbxnagXAfdo7DgEAgExNaYye9BKADw7O8VrtUTObO/VMAAAgS+6+2Xp65tuKFbXJvH7SMwBerb6WwR8AgOZkZgdry5ZFk3395JcAQjh9WokAAEAuXJr0WD35AuD+P6aVBgAA5MOssQUg9vU938yeNf1EAAAgayYtjEuXnjKZ105uBiCExTNKBAAA8hHjmybzsskVALM3zCgMAADIyxsn86ID3gY4fvvfRjObM/NMAAAgS+6+zWq1w21kpLq/1x1wBsDr9Vcz+AMA0BrMbK66u195oNcdeAnAfVJTCQAAoDm4+wGX7idTAFj/BwCgtRzww/t+rwEYf/rfBpviUwMBAEA67h6tVjvCRkYe39dr9jsDYO6vZvAHAKC1mFnw7u5X7e81+y0AHuOk9xQGAABNxH2/Y/iBrgF4TQOjAACA/Ox3DN/n9H4slQ6R+0Yzm/zzAgAAQFNwaUxmh4Whoa0T/X7fg3uMr2LwBwCgNZnUJWmf+wHse4APYb8XDwAAgCYX4z7H8v19wv/DDKIAAID8vGJfv5iwAPjy5UHSyzKLAwAAMmdmp/k+rvebuAD87GenmtSTbSwAAJCxQ33p0pMn+sW+lgCY/gcAoB24TzimT1wAzF6eaRgAAJCPKRUA6bQMowAAgLy4T/ih/mkXBvjg4BwfG9s8fv8gAABoYe5es1qtx0ZGqrv//GkzAD429jwGfwAA2oOZzfLu7j/Y++dPKwDm/qJ8IgEAgFxMMLY/fQbAjAIAAEA7mWBsn+giwBfnEAUAAOTlQDMA4zsAPi+3QAAAIA8v2HtHwD0LwL33LjTpoHwzAQCALJnZPB8Y+L3df7ZHAbBC4dRcEwEAgHzEuMcYv+cMgPtz800DAABysscYv/dFgMwAAADQhuwABYAZAAAA2pDv9SH/dwXAly8Pcp/wkYEAAKDlnbL7nQBPFYD77nu2mc1JkwkAAGTJzOZ5qbRg1/e7LwGckCAPAADIie021j9VAOp1CgAAAG3MJywAISxMkgYAAORi4hkAlgAAAGhr7k4BAACgA01QANyfkyQKAADIy+/v+iJIkvf3H2lmc9PlAQAAWTOzg31w8DBpVwFwPz5tJAAAkAev1Y6Xdi0BFAoUAAAAOoHZs6RdBYAZAAAAOsP4mL+zAIy3AQAA0OaYAQAAoAPtMQMgHZswCgAAyM+x0lMF4JiEQQAAQF7MjpaeKgBHJ4wCAADy4n6MJJkvWtTlz3xm1SRLnQkAAGTL3aOdeOKs4MceezSDPwAAncHMgt9335FBrP8DANBZYjwmqFA4KnUOAACQoxCOCnI/PHUOAACQq8ODzA5LnQIAAOQoxsOCYqQAAADQWQ5jBgAAgM7DEgAAAB3H7LAg90NT5wAAALk6LMjs4NQpAABArnqC3A9KnQIAAOTIfW6Q2dzUOQAAQI7MDgpypwAAANBJ3OcGSSwBAADQSczmBknMAAAA0EnGrwGYkzoHAADI1Zwg967UKQAAQI7MuoKkQuocAAAgPyYVKAAAAHQYd+8KMqMAAADQWZgBAACgA1EAAADoOOMXAQIAgA4TJNVThwAAADlyH6MAAADQeepB7hQAAAA6S50ZAAAAOoyZsQQAAECncakeZDaWOggAAMiR+1iQ+/bUOQAAQK62B0nbUqcAAAA5MtsWJD2ZOgcAAMiR+7YgM2YAAADoJGbbgtwpAAAAdBL3J4PMWAIAAKCTjM8AbE6dAwAA5GpLkNnjqVMAAIBcbQpy35Q6BQAAyNVGCgAAAJ3GfVNQCBQAAAA6C0sAAAB0nBA2BZltTJ0DAADkamNQvb4hdQoAAJCjGDcESetT5wAAADkKYX2whx/+rUueOgsAAMieS3VbuPCRYDffPCb3x1IHAgAAOXB/1C67LIbxb1kGAACgE5itl6Sw+zcAAKDt7VYApIcTBgEAAPl5WBovACY9mDYLAADIhfuD0ngB8PFvAABA23uqAMiMAgAAQCdwf0DatQQw/g0AAGhz4x/6dy4BFArMAAAA0AGsVntAkmzXD2KxuNXM5qaLBAAAsuTum0Olcoj01G2AkvTzRHkAAEAezO7b9eXuBWBdgigAACAv7r8b658qALu1AgAA0JYmKAC7tQIAANCWnl4AjCUAAADamk14DUC9TgEAAKCN+YRLACef/IBLTyZJBAAAMuXSFiuXf73r+6eWAC67LEr6aZJUAAAgW+4/Nsl3fRv2+vXdOccBAAA5MOme3b/fuwDcIwAA0HbcbI8P+XsWAHdmAAAAaE/7mQFwZwYAAIB2ZLbvAmAnnXSfu2/LNxEAAMiSS1tsaOj+3X+2ZwHYeSfAD/MMBQAAMnfX7ncASE+/CFAyuzO3OAAAIHvuTxvbn1YAbIIXAQCAFjbBh/unFQAvFP5PPmkAAEAu6vUDFwBt2PBDl8ZyCQQAADLl7jWr1592m//TCkBYu3aHpB/nkgoAAGTL7G4bGanu/eOnzwDsdFvGcQAAQD4mHNP3VQBuzTAIAADIi9mEY/rEBWAfLwYAAC1mKgXAFi68x903Z5sIAABkyd032apVP5nodxMXgJ07Av5XpqkAAEDWbtt7B8Bd9nUNgMR1AAAAtLp9juX7KwC3ZBAEAADkxKTv7Ot3+y4AZt91qZ5JIgAAkCl3r6mn53v7+v0+C0Aol58w6QfZxAIAABm7w1as2LavX+5vCUAufbvxeQAAQObM9juG77cAyP3mhoYBAAD5iHG/Y/j+C0C1+h3fx+0DAACgObl7VAj7vZh/vwUgjI4+JumuhqYCAABZuyOUy0/s7wX7nwHY6esNCgMAAPJxwLH7gAXA3L/RmCwAACAXkxi7DzwDMGvWLe6+vSGBAABAplzaYmNj3z/Q6w48A7By5XbtZychAADQRNxvtpGR6oFeNplrACQzlgEAAGgFkxyzJ1sAvjajMAAAIC9rJ/Mim+zRYql0v0nPnn4eAACQJZd+Fsrlkybz2snNAOx0wzTzAACAPLh/dbIvnXwBMKMAAADQzKYwVk++ADzyyLfcfeu0AgEAgEy5+xM2b96kH+I36QIQ1q7dIbNvTi8WAADI2NdtxYraZF88lWsAZO7XTz0PAADInNmXpvLyKRUAr1a/7NLY1BIBAIAsuVS1avUrU3nPlApAGB19TO7fmlosAACQsW/ayMjjU3nDlAqAJMns81N+DwAAyNKUx+apF4B6/Xp3j1N+HwAAaDiXxrRjx5Sv0ZtyAQirV6+X2S1TfR8AAMjETWF09LGpvmnqMwA7rZnm+wAAQCO5f246b5teAdixY4S7AQAASMulqkmj03nvtApAGB3dIHc2BQIAICX3tVapbJzOW6e7BCBJlRm8FwAAzNy0x+JpFwCr1b7o0pPTfT8AAJg+l7aoWv3ydN8//QIwMrJF7lPadQgAADSI+/VhdHTaH8RnsgQgua+c0fsBAMD0hPBvM3r7TN5sY2P/4dJDMzkGAACYGnd/wBYuvHEmx5hZARgZqZu0aibHAAAAU7bSLrtsRrvyzmwJQJJLn5npMQAAwOS45CZ9dqbHmXEBCOXyT939ezM9DgAAmAT3m61S+flMDzPjAiBJMmMWAACAPITQkDG3IQXAqtXV7r65EccCAAATc/dN2r59pBHHakwBGBnZIi4GBAAgaytncu//7hqzBCBJIVzdsGMBAICnMfdrGnWshhWAMDT0I5duadTxAADAHm624eGfNOpgjZsBkKQYG9b/Ty8bAAASX0lEQVRMAADAU9y9oTPtjS0AGzeOurShoccEAKDDubTeenq+0MhjNrQAhLVrd0i6tpHHBACg05l0ja1YUWvkMRs7A7DTP7t7Q0MCANCpXNrh9XrDL7RveAEI5fLDMvtco48LAEAnMvfVYfXq9Y0+bhYzADL3j2VxXAAAOo2HkMmYmk0BqFTucOm7WRwbAIBO4e43haGhu7I4diYFQJLkfmVmxwYAoBNkOJZmVgDsxBOvd/d7szo+AADtzKW7bXj4hqyOn10BuOyyKLPLszo+AABt7nKTPKuDZ7cEIMmq1X9z6aEszwEAQLtx6UGbN6+S5TmyLQAjI1VJV2V5DgAA2tCVjd74Z2+ZFgBJ0uzZ17j7pszPAwBAG3DpMZl9OuvzZF4AwnXXbZb0yazPAwBAm7gqDA1tzfok2c8ASDLpY+7+RB7nAgCgVbm0UdLH8zhXPgWgUtkos0/kcS4AAFrYVaFczuUDcy4FQJK0YwezAAAA7IO7b7JqNZdP/1KOBSCMjj4mrgUAAGBfrrKRkcfzOll+MwCSVK1eySwAAAB7cvdNNmtWbp/+pZwLQBgdfUxmV+R5TgAAWsBHbeXKXG+Zz3cGQJJVq1e6tCHv8wIA0Izc/TfW05Prp38pRQEYGdki6SN5nxcAgCb1YVuxYlveJ829AEiSHn30apceTHJuAACahLv/wnp6VqQ4d5ICENau3SH3y1KcGwCAphHC32S95/8+T53ipJJktdpnXbo71fkBAEjJ3e+yhQuHUp3fUp1YkmKx+GYz+/eUGQAASMGl14dy+cZU5082AyBJoVL5mrt/I2UGAADy5u5fTTn4S4kLgCQpxve5e0wdAwCAPLg0pkLhz1PnSF4AwurV/1dmn0mdAwCAXLivCKtW/Th1jOQFQJKsq+tD7r45dQ4AALLk7ptUrf5N6hxSsxSAlSt/I7O/S50DAICMLQ+jo02xG25TFABJsnnzrnL3n6bOAQBAFlz6odVq/5Q6xy7NUwBWrKjJ7M9S5wAAIBMxXmQjI/XUMXZpmgIgSaFc/rq7X586BwAAjeTSmjA8fHPqHLtrqgIgSVavX+LSk6lzAADQCO6+VdL7UufYW/MVgDVr7pf04dQ5AABokOWhXP5V6hB7a7oCIEk2b97lPCcAANDqXPqB1WpXpc4xkeYsACtW1OT+Dpc8dRYAAKZjfJfbZc104d/umrIASFKoVL4r6V9S5wAAYJr+OZTL/5U6xL40bQGQJHP/C5fWp84BAMBUuPSQzD6YOsf+NHcBqFQ2SmJvAABAq3lnKJefSB1if5q6AEhSKJc/59IXUucAAGAyXFodyuUvp85xIE1fACRJ9fq7XHosdQwAAPbHpQ0W40Wpc0xGSxSAsHr1ekkXp84BAMB+uV9kw8OPpI4xGZY6wFTEUukrJp2eOgcAAHtz9y+GSuVtqXNMVkvMAOxmGUsBAIBm49IjivGdqXNMRUsVgFAuPyyppf6CAQAdYdn4cnXLaKkCIP3uroBK6hwAAEiSS58N5fIXU+eYqpYrAJJkXV3vdveme7ACAKCzuHS/WvQi9dYsACtXbpLZuTwrAACQirtHuQ82+4Y/+9KSBUCSQrl8o6QrU+cAAHSsj4ZK5dupQ0xXyxYASbJq9QOS7kidAwDQWdz9Vvv1r/9X6hwz0doFYGSk6mZ9Lm1JnQUA0DEet3q9326+eSx1kJlo6QIgSWFoaJ3c35U6BwCgM7j7O2zNmvtT55ipli8AkhQqlVUurUqdAwDQ3lz611CprEmdoxHaogBIklWr73LpJ6lzAADak0t327x5bfOI+pZ6FsCBxL6+UxXCbWY2N3UWAED7GL/W7KWhXP5p6iyN0jYzAJIUVq++W2bvSJ0DANB2/rSdBn+pzQqAJIVyecjdr02dAwDQHtz9k6Fc/lzqHI3WdgVAkvTYYxeL/QEAADPk7rdaT8+lqXNkoa2uAdhdLBafLbPbTToydRYAQOtxab12rvu35bNn2nMGQFKoVH4p97e71NIbNQAA8ufuNYtxSbsO/lIbFwBJCpXKt+TellM3AIAMuV9sw8O3pI6RpbZdAthdLJU+Y9K5qXMAAJqfS58O5fKy1Dmy1tYzAL/z6KMXuHRb6hgAgObm0vetWr0wdY48dEQBCGvX7pD0Vndv27UcAMDMuPRLmb3VRkaqqbPkoSMKgCSFcvlhk85w962pswAAmou7b5bZ6WFo6Leps+SlYwqAJFml8gO597t7TJ0FANAcXKpLOjsMDf0odZY8dVQBkKQwPPwVSe9PnQMA0DQuCZXK11KHyFtH3AUwkVgsXmM8NwAAOpq7fypUKhelzpFCx80A7GK12rtduiF1DgBAGu5+vZ144sWpc6TSsTMAkuTLls31rVu/ZdJpqbMAAPLj0ve1Y8frwujok6mzpNLRBUCS4pIlR6m7+3tmdkLqLACA7Ln7vSoUXhlWrXo0dZaUOnYJYJcwOrpBIbzZpQ2pswAAsuXSeoWwuNMHf4kCIEkKQ0PrFMIfu/vm1FkAAJl5XPX6m8PQ0C9SB2kGFIBxYdWq283sTHffnjoLAKCxXHrSpTPC6tV3ps7SLCgAu7Fy+SaZnc0jhAGgfbh7TTsf7fud1FmaCQVgL6Fc/rLM/tQlT50FADAz7h5lNhiGh/89dZZmQwGYQBga+jdJHXtvKAC0DfcLQ7k8nDpGM6IA7EMolz/pbBkMAC3LpUvC8PDVqXM0KwrAfoRy+XKXPpQ6BwBgajzGvwzl8lWpczQzCsABhHL57939b1PnAABMjkvLw/Dw/06do9l1/E6AkxVLpY+Y9FepcwAA9s2lD4dy+X+lztEKKABTQAkAgObF4D81LAFMQSiXP8ByAAA0H5f+msF/apgBmIZYKn3QpA+nzgEAGL/gjzX/KaMATFMslf7cpI+mzgEAncylS7jaf3ooADMQS6WLJH3c+HsEgFy5e5T7hdznP30MXDMUi8WlMrvOpK7UWQCgE7h7TWaD7PA3MxSABoil0plyX2Nmc1JnAYB25tKTinEJe/vPHAWgQbxU+iN3/7KZHZw6CwC0qcddOoOn+jUGBaCB4tKlL1WM/27SUamzAEA7cWm96vU3h9Wr70ydpV1QABosnn32QhUKa83shNRZAKAduPu9CmFxGBr6Reos7YSNgBosrFlzn6rVV7p0W+osANDq3P17KhReyeDfeBSADITR0Q02b97/49INqbMAQKty9+tVrb4+rFr1aOos7YgCkBFbsWKbVatvdfdrU2cBgFbj7p+yE088K4yOPpk6S7viGoAcxGLxEkn/aGYULgDYD5fqMntPGBr6VOos7Y4CkJPY33+GQqiY1JM6CwA0I3ffLOnsUKl8LXWWTkAByFEcGHiB3L9i0vGpswBAM3HplzI7PQwN/Sh1lk7BlHSOwtDQXdbVdRp3CADAU1z6vur1lzP454sZgATi4sWzNX/+NSadmzoLAKTk7v9itdq7bWSkmjpLp6EAJDT+NMEreZAQgE7j7jW5X8zT/NKhACTmpdIfuTRi0pGpswBAHlxabzEuseHhW1Jn6WRcA5CYlcs3yf2l7n576iwAkDV3//8kvZTBPz0KQBMIlcov9dhjr3KJqTAAbcvdP2k9Pa8O5fKvUmcBSwBNJ/b3l2R2rZnNS50FABrB3TfL7H+GcvlzqbPgKRSAJhRLpedK+rxJJ6fOAgAz4e4/ktmSUC7/NHUW7IklgCYUyuV7rFp9mdxXps4CANPl0r9aT8/LGfybEzMATW58SeBqMzs4dRYAmKTH3f0doVJZkzoI9o0C0ALiwMAJinHYzF6aOgsA7I+736oQimFo6Beps2D/WAJoAWFoaJ319LzSpStc8tR5AGBv7h7d/f+1X//61Qz+rYEZgBYTBwZeK/fP8kAhAM3CpfvlPhgqlW+nzoLJYwagxYShof+0avV57j6UOgsAuPRZzZ79fAb/1sMMQAuLpdISuV9jZvNTZwHQWVzaYGbLbGjo+tRZMD0UgBYXS6Vjx0vAmamzAOgM7v5FxfjOsHr1+tRZMH0UgDYRi8WipE8wGwAgKy5tkHQhO/q1BwpAG4kDA0crxn8ysyWpswBoLy6tthgvsuHhR1JnQWNQANpQLJWWSPqUScekzgKgtbn0kNzfFSqVL6XOgsbiLoA2FMrlUevqOtndr2XfAADTMX5f/6ckncLg356YAWhzsb//FTJbYWZ/kDoLgNbg0g8kLQvl8n+lzoLsUAA6gC9a1OXHHXepzP7azOamzgOgObn7VknLrVa7ykZG6qnzIFsUgA7iS5c+y+v1K83srNRZADQXl9ZIel8ol3+VOgvyQQHoQLFUep3cP2lmp6TOAiAtl35o0p9ZuXxT6izIFxcBdqBQLt9oPT0vcOlSd38idR4A+XP3Te5+sVWrL2Lw70zMAHS42Nd3jAqFv5X0pyYVUucBkC2XxuS+QtXq34TR0Q2p8yAdCgAkSbGv71QVCleY9KbUWQBkw92/au7vs+Hhn6TOgvQoANhD7O9/k8z+kdsGgfbh7nfJ7NJQLt+YOguaB9cAYA9hePg/rFZ7oZud7+4PpM4DYPrc/RduNmgnnvhiBn/sjRkA7FNcvHi25s+/QNIHTToqdR4Ak+Puv5H0YavVPm0jI9XUedCcKAA4IO/t7fFZs94j6c/N7JDUeQBMzN03Sfqo9fR83Fas2JY6D5obBQCT5sXi4S5dIuliigDQPMYH/qts1qyP28qVm1LnQWugAGDKxovAe8zsYkmHps4DdCqXNkq6yqrVj9vIyOOp86C1UAAwbT44eJjXahfL7GKTDk+dB+gULj0m6SpJHw/lMpt5YVooAJgx7+3t8e7uZXK/xMyemToP0K5celDSFTL7lzA0tDV1HrQ2CgAaxpctm+Xbtg3I/f0mnZw6D9AuXLpbZh+1uXOHbcWKWuo8aA8UADScS+bF4pkye69Jr0mdB2hV7n6T3K+04eEbTPLUedBeKADIVOzre5FCeI/M+kzqTp0HaHYu7ZA0LLOrwtDQXanzoH1RAJALHxx8htdq75R0gZkdnToP0GxcWm/SNV6vXx1Wr16fOg/aHwUAufLe3m7v7j5L0gUsDwDj0/zSNdbT8wXW95EnCgCSiaXSc+V+gZmdI/YTQAcZ37hnpblfw5P5kAoFAMn5smVztWXL210638xenToPkAWXXO43K4TPaPv2kTA6+mTqTOhsFAA0lTgwcIJiPFfSIHsKoB2MP1VzpUmftUrl56nzALtQANCUfPny4Pfe+waFsFTubzWzeakzAZPl0ha5X68Q/s0WLrzRLrssps4E7I0CgKbny5bN9a1b3yKpKPc3mdms1JmAvblUlftaSRVVq19mih/NjgKAlhKXLDlCs2f3yv3tMltkUiF1JnQul8Yk3ST3z5k0apXKxtSZgMmiAKBleX//kW72FklLJL2OmQHkwaWqpG/KbFRmXw6rVj2aOhMwHRQAtIXxJxOeIektkt5oZgenzoT24e5PSPq6zL5k1epXePQu2gEFAG3He3u7NWvWa9zsDEmnm/T7qTOh9bj7Okk3yOwGmzfv22zSg3ZDAUDbi0uXnqIY3yTpjXJfZGZzU2dC83H3rZJuktk3JK0N5fJPU2cCskQBQEfx3t5udXe/0t3fIOmNkl5sZiF1LuTP3aOkOyR9Xe7fsIMP/h6f8tFJKADoaN7be6h3d79K7oskvUZmLzGpK3UuNJ5LY3K/XWbfVow329jYd1nLRyejAAC7iQMD8yS9UjG+StIrzOw08ZyCljS+3/5tkm416TsewvfD0NDW1LmAZkEBAPbDJfOlS0+W+x+O//NySc/llsPm4u41md0t6TaZ3SqzW23Vqp+Y5KmzAc2KAgBMUVy8eLbmzz9V7i+S2Yvk/iJJL2C74ny4tEXSXXK/U2Z3ql6/0+r1u21kpJo6G9BKKABAA7hkPjDwe4rxVEnPNem5Lp0q6RSKwfSM76f/Y5Pu8Z2f7u+xsbG7tWbNL/lkD8wcBQDIkEvmpdICk05w6QSTTnD3EySdIOn3O33DInffLLP7tPOe+3WS1pnZfS6ts3L51wz0QHYoAEBC4zsYHi+zZ8n9qT+lY2V2tNyPkXRkq92qOH6L3SMyWy9pvaSH5f6gpAfl/oDMHrRa7QGuwgfSoQAATc6XLw9+331HKsZjFMJRkg5XjIdJOkzS4TLb9XWP3OfK7KDxP+fKfa6kOTLrMqng7l3a+QClgsx23u7oPiapLqluZmMu1cd/tl1m2+S+bfzPJ2W2TTvX4DdJ2qidV9pvUgg7v49xg0JYbwsXPsIjcIHm9v8DO9dcT//RiDMAAAAASUVORK5CYII="

        return t.substitute({
            "title": self.title,
            "img": img,
            "imgs": imgs,
            "footnotes": self.render_footnotes()
        })