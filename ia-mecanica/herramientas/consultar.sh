#!/bin/bash
# Script para consultar la base de datos fácilmente
# Uso: ./consultar.sh "SELECT * FROM tabla"

curl -s -X POST http://localhost:5000/consultar \
  -H "Content-Type: application/json" \
  -d "{\"consulta\": \"$1\"}" | python3 -m json.tool
