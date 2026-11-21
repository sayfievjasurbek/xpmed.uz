"""Contents-derived HALL families; physical PDF pages checked against source headings."""
O=['orthopedics','traumatology'];N=['spine','neurosurgery'];E=['ent'];C=['cardiothoracic']
SECTIONS=[
('hall-titan','HALL Titan','HALL Titan',[8],O,'Large Bone & Small Bone Orthopedics','Ортопедия крупных и мелких костей'),
('hall-batteries-and-accessories','Batteries & Accessories','Аккумуляторы и принадлежности HALL',[9],O,'',''),
('hall-powerpro','PowerPro & PowerPro Electric II','PowerPro и PowerPro Electric II',[10,11],O,'Large Bone & Small Bone Orthopedics','Ортопедия крупных и мелких костей'),
('hall-pin-and-wire-drivers','Pin and Wire Drivers','Драйверы для спиц и штифтов HALL',[12],O,'Large Bone & Small Bone Orthopedics','Ортопедия крупных и мелких костей'),
('hall-attachments','Attachments','Насадки HALL',[13],O,'Large Bone & Small Bone Orthopedics','Ортопедия крупных и мелких костей'),
('hall-sterilization-trays','Sterilization Trays','Лотки для стерилизации HALL',[14],O,'Large Bone Orthopedics','Ортопедия крупных костей'),
('hall-pro-blades','HALL Pro Blades','Лезвия HALL Pro',[15,16,17],O,'Total Knee Arthroplasty','Тотальное эндопротезирование коленного сустава'),
('hall-intrex-blade-system','Intrex Blade System','Система лезвий Intrex',[18],O,'Total Knee Arthroplasty','Тотальное эндопротезирование коленного сустава'),
('hall-m-class-blades','M-Class Blades','Лезвия M-Class',[19],O,'Total Knee Arthroplasty','Тотальное эндопротезирование коленного сустава'),
('hall-classic-blades','HALL Classic Blades','Лезвия HALL Classic',[20],O,'Total Knee Arthroplasty','Тотальное эндопротезирование коленного сустава'),
('hall-large-bone-knee-blades','Large Bone Knee Blades','Лезвия для эндопротезирования коленного сустава HALL',list(range(21,32)),O,'Total Knee Arthroplasty','Тотальное эндопротезирование коленного сустава'),
('hall-stryker-compatible-replacement-blades','Stryker Compatible Replacement Blades','Сменные лезвия, совместимые со Stryker',[32,33],O,'Total Knee Arthroplasty','Тотальное эндопротезирование коленного сустава'),
('hall-large-bone-oscillating-blades','Large Bone Oscillating Blades','Осциллирующие лезвия HALL для крупных костей',list(range(34,40)),O,'Total Joint Arthroplasty & Large Bone Trauma; ACL Blades','Тотальное эндопротезирование суставов и травматология крупных костей; лезвия для реконструкции ПКС'),
('hall-large-bone-reciprocating-blades','Large Bone Reciprocating Blades','Реципрокные лезвия HALL для крупных костей',[40,41],O,'Total Joint Arthroplasty & Large Bone Trauma','Тотальное эндопротезирование суставов и травматология крупных костей'),
('hall-microfree-power-system','HALL MicroFree Power System','Силовая система HALL MicroFree',[42,43],O,'Small Joint','Хирургия мелких суставов'),
('hall-micropower-plus','MicroPower +','MicroPower +',[44],O,'Small Bone','Хирургия мелких костей'),
('hall-attachments-and-bur-guards','Attachments & Bur Guards','Насадки и защитные тубусы для боров HALL',[45],O,'For Use with Micro Handpieces','Для микронаконечников'),
('hall-micro-sagittal-saw-blades','Micro Sagittal Saw Blades','Лезвия для микросагиттальных пил HALL',list(range(46,52)),O,'',''),
('hall-micro-oscillating-saw-blades','Micro Oscillating Saw Blades','Лезвия для микроосциллирующих пил HALL',[52,53,54],O,'',''),
('hall-micro-reciprocating-saw-blades-and-rasps','Micro Reciprocating Saw Blades & Rasps','Лезвия и рашпили для микрореципрокных пил HALL',[55],O,'',''),
('hall-micro-burs','Micro Burs','Микроборы HALL',[56,57,58],O,'',''),
('hall-sternum-saws','Sternum Saws','Стернальные пилы HALL',[59],C,'Sternotomy','Стернотомия'),
('hall-sternum-saw-blades','Sternum Saw Blades','Лезвия для стернальных пил HALL',[60,61,62],C,'Primary & Repeat Sternotomy','Первичная и повторная стернотомия'),
('hall-ultrapower-burs','UltraPower Burs','Боры UltraPower',[63,64,65,66,67,68],E+N,'Otology (Round Burs Only), Spine & Neuro','Отохирургия (только шаровидные боры), хирургия позвоночника и нейрохирургия'),
('hall-e9000-system','E9000 System','Система E9000',[70],E+N,'ENT, Spine & Neuro','ЛОР-хирургия, хирургия позвоночника и нейрохирургия'),
('hall-e9005-ent-shaver-blades','E9005 ENT Shaver Blades','Шейверные насадки E9005 для ЛОР-хирургии',[69,71,72,73],E,'Sinus Surgery','Хирургия околоносовых пазух'),
('hall-e-burs','E Burs','Боры серии E',[74,75],E+N,'Otology, Spine & Neuro','Отохирургия, хирургия позвоночника и нейрохирургия'),
('hall-osteon','Osteon','Osteon',[76],E,'ENT','ЛОР-хирургия'),
('hall-osteon-burs','Osteon Burs','Боры Osteon',[77],E,'Otology','Отохирургия'),
('hall-electric-consoles-and-accessories','Electric Consoles & Accessories','Электрические консоли и принадлежности HALL',[78],[],'','')]
MATRIX_BLADES=set(range(15,21))|{32,33}
ROW_BLADES=set(range(21,32))|set(range(34,42))|set(range(46,56))|{60,61,62}
BUR_MATRICES={56,57,58,64,65,66,67,68,74,75,77}
