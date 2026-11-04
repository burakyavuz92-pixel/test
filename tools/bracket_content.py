"""Bracket contents are text first; physical meaning is parsed separately."""
import re

def compact(text):return re.sub(r'\s+','',text).replace('×','X').replace('x','X')
def literal(text):
 text=compact(text);num=r'\d+(?:[.,]\d+)?';number=lambda x:float(x.replace(',','.'))
 m=re.fullmatch('('+num+r')X('+num+r')°',text)
 if m:return {'nominal':number(m[1]),'displayText':text,'chamferAngleDeg':number(m[2])}
 m=re.fullmatch(r'([Øø⌀R]?)('+num+r')(?:±('+num+r'))?',text)
 if not m:raise ValueError('Unsupported bracket measurement: '+text)
 result={'nominal':number(m[2])}
 if m[1] in ('Ø','ø','⌀'):result['diameterSymbol']=True
 if m[3]:result['tolerance']={'kind':'symmetric','upperDeviationMm':number(m[3]),'lowerDeviationMm':-number(m[3])}
 return result
