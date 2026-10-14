# Base de conhecimento

`techcorp/`: corpus da empresa fictícia TechCorp Banco Múltiplo, usado no Lab 2 (27 documentos: os 6
da v1 e 21 escritos na Sessão 4). Cada documento começa com um cabeçalho de permissão: `nivel`
(Público < Interno < Regulado), `dono` e, às vezes, `departamentos` (restrição por documento). Os
documentos Regulados têm um fato-canário que só existe neles, para detectar vazamento. Tudo é
sintético. Do professor: não editar (o `make lab2-check` confere).
