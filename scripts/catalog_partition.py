"""Require explicit, disjoint source ranges before touching a shared catalog cache."""
def disjoint_partition(section,profile,previous):
 return bool(section and profile and profile.get('partition')==section and profile.get('authorizedPhysicalPages') and previous.get('sourcePages') and not set(previous['sourcePages'])&set(profile['authorizedPhysicalPages']))
def validate_partition_evidence(profile,evidence):
 if not profile.get('partition'):return
 authorized=set(profile.get('authorizedPhysicalPages',[]));provided={p['page']for p in evidence};required={p for s in profile.get('systems',[])for p in s.get('sourcePages',[])}
 if not authorized or not provided<=authorized or not required<=provided:raise ValueError('Partition evidence must cover every system and stay inside its authorized pages')
