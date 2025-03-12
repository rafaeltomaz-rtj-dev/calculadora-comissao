Write-Host "🚀 Iniciando Deploy da Calculadora de Comissão..." -ForegroundColor Green

# Adicionar todos os arquivos ao Git
git add .

# Commit com mensagem padrão ou personalizada
if ($args.Count -eq 0) {
    git commit -m "Atualizando código do dashboard"
} else {
    git commit -m $args[0]
}

# Enviar para o GitHub
git push origin main

Write-Host "✅ Deploy concluído! Agora reinicie o app no Streamlit Cloud." -ForegroundColor Green
