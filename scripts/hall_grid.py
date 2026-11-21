"""Recover real table cells from neutral-gray source vector rules, not OCR text order."""
from collections import defaultdict
import math

def source_bands(page):
 vertical=[];horizontal=[];frames=[]
 for d in page.get_drawings():
  c=d.get('color')
  if not c or max(c)-min(c)>.07 or not 0<=sum(c)/3<.9 or d.get('width',2)>1.1:continue
  for item in d['items']:
   if item[0]=='re':
    r=item[1]
    if r.width>page.rect.width*.16 and r.height>8 and r.y0>page.rect.height*.12:frames.append(r)
    continue
   if item[0]!='l':continue
   p,q=item[1:];x0,x1=sorted([p.x,q.x]);y0,y1=sorted([p.y,q.y])
   if abs(x1-x0)<.2 and y1-y0>4:vertical.append((x0,y0,y1))
   elif abs(y1-y0)<.2 and x1-x0>15:horizontal.append((y0,x0,x1))
 groups=[]
 for x,y0,y1 in sorted(vertical,key=lambda a:(a[1],a[2],a[0])):
  g=next((g for g in groups if abs(g['top']-y0)<.8 and abs(g['bottom']-y1)<.8),None)
  if g:g['xs'].append(x)
  else:groups.append({'top':y0,'bottom':y1,'xs':[x]})
 result=[]
 for g in groups:
  xs=[]
  for x in sorted(g['xs']):
   if not xs or x-xs[-1]>.8:xs.append(x)
  cover=[r for r in frames if r.x0<=xs[0]+1 and r.x1>=xs[-1]-1 and r.y0<=g['top']+.8 and r.y1>=g['bottom']-.8]
  if cover:
   frame=min(cover,key=lambda r:r.get_area());xs=sorted(set([frame.x0,frame.x1]+xs));xs=[x for i,x in enumerate(xs)if not i or x-xs[i-1]>.8]
  if len(xs)<3 or xs[-1]-xs[0]<page.rect.width*.16 or g['top']<page.rect.height*.12 or g['bottom']>page.rect.height*.94:continue
  cuts=sorted({g['top'],g['bottom']}|{y for y,a,b in horizontal if g['top']+.8<y<g['bottom']-.8 and a<=xs[0]+2 and b>=xs[-1]-2})
  for top,bottom in zip(cuts,cuts[1:]):
   if bottom-top>5:result.append({'top':top,'bottom':bottom,'xs':xs})
 return sorted(result,key=lambda a:(a['top'],a['xs'][0]))
