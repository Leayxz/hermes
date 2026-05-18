# API de Locação de Carros - Avaliação Desenvolvedor Python

## 🎯 Tarefa da Avaliação

**Implementar um Sistema de Recompensas para Clientes** nesta plataforma de locação de carros.

### Visão Geral
- **Prazo**: Até 3 dias (considerando que você pode ter um emprego diurno)
- **Funcionalidade**: Sistema de pontos de recompensa onde clientes ganham pontos baseados em atividade de locação
- **Objetivo**: Avaliar suas habilidades de entrega, qualidade de código, testes e documentação

## 📖 Começando

1. **Leia a Especificação da Funcionalidade**:
   - Veja **[FEATURE.md](FEATURE.md)** para requisitos completos
   - Revise critérios de aceitação e diretrizes de avaliação

2. **Configure o Ambiente**:
   - se estivar usando windows: `setup.cmd`
   - se estiver usando sistema baseado em unix: `./setup.sh`

3. **Revise o Código Existente**
   
4. **Planeje Sua Implementação**

5. **Implemente & Documente**:
   - Construa a funcionalidade
   - Use **`IMPLEMENTACAO.md`** para documentar suas decisões

## 📁 Estrutura do Projeto

```
carro_facil/           # CÓDIGO DA APLICAÇÃO
├── FEATURE.md         # 📋 Especificação da funcionalidade (LEIA!)
├── IMPLEMENTACAO.md   # 📝 Documente seu trabalho aqui
├── rentals/           # App principal Django
├── car_rental/        # Projeto Django
└── ... (todo código Python)
```

## 📦 O Que Submeter

1. **Código**: Todas as mudanças no diretório raiz
2. **Documentação**: Atualizar `IMPLEMENTACAO.md` com:
   - Suas decisões de design
   - Como testar sua funcionalidade
   - Suposições feitas
   - O que você melhoraria com mais tempo
3. **Testes**: Garantir que todos os testes passem


## 📚 Arquivos Principais para Ler

1. **[FEATURE.md](FEATURE.md)** - Especificação completa da funcionalidade
2. **[DOCKER.md](DOCKER.md)** - Guia de uso do Docker
3. **[README.md](README.md)** - Documentação da aplicação

## 💡 Dicas

- Comece pequeno - faça os pontos básicos funcionarem primeiro
- Escreva testes cedo, não no final
- Documente seu raciocínio e decisões
- Use o Django admin para testar manualmente
- Faça perguntas documentando suposições

## ❓ Dúvidas?

Se os requisitos não estiverem claros e não pudermos responder:
1. Faça suposições razoáveis
2. Documente-as em IMPLEMENTACAO.md
3. Explique seu raciocínio

---

## Endpoints da API Atuais (Existentes)

URL Base: `http://localhost:8000/api/`

- `GET /` - Mensagem de boas-vindas
- `GET /cars/` - Listar carros disponíveis
- `GET /cars/{id}/` - Detalhes do carro
- `POST /rentals/create/` - Criar locação
- `POST /rentals/{id}/return/` - Devolver carro
- `GET /rentals/` - Listar todas as locações
- `GET /rentals/customer/{email}/` - Locações do cliente
- `GET /stats/` - Estatísticas de locação

**Sua tarefa**: Adicionar endpoints de recompensas! Veja FEATURE.md para especificações.

---

Boa sorte! Estamos ansiosos para ver sua solução! 🚀

Se você tiver dúvidas sobre a configuração, verifique os arquivos de documentação e se ainda estiver em dúvida, responda o e-mail que enviamos fazendo suas perguntas. Tentaremos responder o mais rápido possível.
