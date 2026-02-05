# Changelog - DeepCool AK Series Digital

## [1.3.0] - 2026-02-05

### ✨ Novas Funcionalidades

#### 💾 Persistência de Configurações do Usuário
- **Configurações salvas automaticamente** em `~/.config/deepcool-digital/settings.json`
- Preferências mantidas entre sessões:
  - Modo de exibição (automático, temperatura, uso de CPU)
  - Unidade de temperatura (Celsius ou Fahrenheit)
  - Configuração de alarme (habilitado/desabilitado e temperatura)
- Validação automática de configurações carregadas
- Função de reset para valores padrão
- **Benefício:** Usuário não precisa reconfigurar a cada login

#### 🔧 Módulo de Utilitários
- **Novo módulo `utils.py`** com funções reutilizáveis
- Funções centralizadas:
  - `celsius_to_fahrenheit()` - Conversão de temperatura
  - `format_temperature()` - Formatação para exibição
  - `validate_temperature_unit()` - Validação de unidade
  - `validate_display_mode()` - Validação de modo
  - `clamp()` - Limitação de valores
- **Benefício:** Elimina código duplicado (princípio DRY)

### 🎯 Melhorias de Código

#### 📝 Type Hints Completos (PEP 484)
- **Anotações de tipo** em todos os módulos:
  - `config.py` - Constantes tipadas
  - `hardware.py` - Funções com tipos de retorno
  - `protocol.py` - Type aliases para modos
  - `driver.py` - Classe com tipos completos
  - `tray.py` - Interface Qt tipada
  - `settings.py` - Gerenciador tipado
  - `utils.py` - Funções utilitárias tipadas
  - `main.py` - Função principal tipada
- **Benefícios:**
  - Melhor legibilidade do código
  - Detecção de erros com `mypy`
  - Autocompletar melhorado em IDEs
  - Serve como documentação

#### 🔒 Gerenciamento Adequado de Arquivos
- **Context managers** para arquivos de lock
- Função dedicada `release_lock()` para liberar recursos
- Garantia de fechamento de arquivos mesmo com exceções
- **Benefício:** Elimina vazamento de file descriptors

#### 🧹 Refatoração de Código Duplicado
- Conversão Celsius/Fahrenheit centralizada em `utils.py`
- Removida duplicação entre `driver.py` e `tray.py`
- Formatação de temperatura unificada
- **Benefício:** Manutenção simplificada e consistência

### 📚 Documentação

#### Docstrings Completas
- Todas as funções e classes documentadas
- Parâmetros e retornos especificados
- Exemplos de uso incluídos
- Exceções documentadas

#### Logging Aprimorado
- Logs mais detalhados em operações de configuração
- Rastreamento de mudanças de configuração
- Logs de salvamento/carregamento de settings

---

## [1.2.0] - 2026-02-05

### ✨ Melhorias Implementadas

#### 🔧 Tratamento de Exceções Robusto
- **Exceções específicas** ao invés de `except Exception` genérico
- Tratamento diferenciado para erros HID, I/O e sensores
- Mensagens de erro claras e informativas
- Logging detalhado de todos os erros

#### 📦 Gerenciamento de Dependências
- **Adicionado `requirements.txt`** com todas as dependências
- Compatível com Python 3.8+

#### 🐍 Generalização da Versão do Python
- **Removida dependência do Python 3.11**
- Suporte para Python 3.8 até 3.12+
- Script de instalação detecta automaticamente a melhor versão

#### 📝 Sistema de Logging
- **Logging estruturado** usando módulo `logging` do Python
- Logs salvos em `~/.config/deepcool-digital/deepcool-digital.log`

#### 🌐 Suporte Expandido a Distribuições
- **Instalador universal** para openSUSE, Debian, Ubuntu e Fedora

---

## Como Atualizar

```bash
# Desinstalar versão anterior
./uninstall.sh

# Baixar nova versão
git pull origin main

# Reinstalar
./install.sh
```

---

## Créditos

**Versão 1.3.0:** Implementada por Manus AI  
**Versão 1.2.0:** Implementada por Manus AI  
**Projeto original:** [marquimRcc](https://github.com/marquimRcc)
