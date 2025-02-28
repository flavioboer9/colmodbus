import streamlit as st
import time
from pymodbus.client import ModbusTcpClient
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Função para verificar se o servidor Modbus está rodando
def verificar_conexao_modbus(host="127.0.0.1", port=5020, timeout=1):
    """
    Verifica se o servidor Modbus está rodando.
    
    Returns:
        bool: True se o servidor estiver rodando, False caso contrário
    """
    print(f"Verificando conexão Modbus em {host}:{port}")
    
    # Criar cliente
    client = ModbusTcpClient(host=host, port=port)
    
    # Conectar
    connected = client.connect()
    print(f"Conexão: {connected}")
    
    if connected:
        # Ler registros para confirmar
        try:
            response = client.read_holding_registers(address=0, count=1)
            success = response is not None and not response.isError()
            print(f"Leitura de teste: {success}")
        except Exception as e:
            print(f"Erro na leitura de teste: {e}")
            success = False
        
        # Fechar conexão
        client.close()
        print("Conexão fechada")
        return success
    else:
        print("Falha na conexão")
        return False

# Função para ler os valores dos registros Modbus
def ler_registros_modbus(host="127.0.0.1", port=5020):
    """
    Lê os valores dos registros Modbus do servidor.
    
    Args:
        host (str): Endereço do servidor Modbus
        port (int): Porta do servidor Modbus
    
    Returns:
        dict: Dicionário com os valores dos registros ou None se ocorrer um erro
    """
    # Criar cliente
    client = ModbusTcpClient(host=host, port=port)
    
    # Conectar
    if client.connect():
        try:
            # Ler registros
            response = client.read_holding_registers(address=0, count=4)
            
            if response is None or response.isError():
                client.close()
                return None
            
            # Extrair valores
            ativar = bool(response.registers[0])
            entregar = bool(response.registers[1])
            gaveta = response.registers[2]
            posicao_gaveta = response.registers[3]
            
            # Fechar conexão
            client.close()
            
            # Retornar valores
            return {
                "ativar": ativar,
                "entregar": entregar,
                "gaveta": gaveta,
                "posicao_gaveta": posicao_gaveta
            }
        except Exception as e:
            print(f"Erro ao ler registros: {e}")
            client.close()
            return None
    else:
        return None

# Inicializar estado da sessão
if 'last_full_refresh' not in st.session_state:
    st.session_state.last_full_refresh = time.time()
    st.session_state.refresh_interval = 30  # segundos
    st.session_state.valores_registros = None
    st.session_state.modbus_host = "127.0.0.1"
    st.session_state.modbus_port = 5020
    st.session_state.servidor_conectado = verificar_conexao_modbus(
        host=st.session_state.modbus_host,
        port=st.session_state.modbus_port
    )
    if st.session_state.servidor_conectado:
        st.session_state.valores_registros = ler_registros_modbus(
            host=st.session_state.modbus_host,
            port=st.session_state.modbus_port
        )

# Adicionar título e botão de refresh na mesma linha
col1, col2 = st.columns([0.9, 0.1])
with col1:
    st.title("Integração Raspberry - FX5")
with col2:
    st.markdown('<div style="height: 25px;"></div>', unsafe_allow_html=True)
    refresh_button = st.button("↻", help="Atualizar agora", key="refresh_button")
    
    # Estilo para o botão
    st.markdown("""
    <style>
    [data-testid="stButton"] > button {
        background-color: #FFB74D;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Verificar se é hora de atualizar automaticamente (a cada refresh_interval segundos)
current_time = time.time()
if current_time - st.session_state.last_full_refresh > st.session_state.refresh_interval:
    # Atualizar o timestamp da última atualização
    st.session_state.last_full_refresh = current_time
    
    # Verificar conexão usando os valores atuais de host e porta
    st.session_state.servidor_conectado = verificar_conexao_modbus(
        host=st.session_state.modbus_host,
        port=st.session_state.modbus_port
    )
    
    # Atualizar valores se o servidor estiver conectado
    if st.session_state.servidor_conectado:
        st.session_state.valores_registros = ler_registros_modbus(
            host=st.session_state.modbus_host,
            port=st.session_state.modbus_port
        )
    
    # Recarregar a página para mostrar os valores atualizados
    st.rerun()

# Usar um container customizado para o conteúdo
custom_container = st.container()

# Dentro do container customizado, criar o HTML para o conteúdo
with custom_container:
    # Adicionar inputs para host e porta com botão de conexão
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        novo_host = st.text_input("Host", value=st.session_state.modbus_host, key="input_host")
    
    with col2:
        novo_port = st.number_input("Porta", value=st.session_state.modbus_port, min_value=1, max_value=65535, step=1, key="input_port")
    
    with col3:
        conectar_button = st.button("Conectar", key="conectar_button")
    
    # Processar o clique no botão de conexão
    if conectar_button:
        # Atualizar host e porta na session state
        st.session_state.modbus_host = novo_host
        st.session_state.modbus_port = int(novo_port)
        # Verificar conexão com os novos valores
        st.session_state.servidor_conectado = verificar_conexao_modbus(host=novo_host, port=int(novo_port))
        # Se conectado, atualizar os valores dos registros
        if st.session_state.servidor_conectado:
            st.session_state.valores_registros = ler_registros_modbus(
                host=novo_host, 
                port=int(novo_port)
            )
        # Recarregar a página para aplicar as mudanças
        st.rerun()
    
    # Adicionar o status de conexão
    status_class = "connected" if st.session_state.servidor_conectado else "disconnected"
    host = st.session_state.modbus_host  # Default host
    port = st.session_state.modbus_port  # Default port
    
    # Definir o texto de status com host e porta
    if st.session_state.servidor_conectado:
        status_text = f"Servidor Modbus Conectado ({host}:{port})"
    else:
        status_text = f"Servidor Modbus Desconectado ({host}:{port})"
    
    # Exibir o status de conexão
    st.markdown(f'''
    <div style="display: flex; align-items: center; margin-bottom: 10px;">
        <div class="connection-status {status_class}"></div>
        <span>{status_text}</span>
    </div>
    ''', unsafe_allow_html=True)
    
    # Adicionar espaço após o status
    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
    
    # Adicionar os valores dos registros se disponíveis
    if st.session_state.servidor_conectado and st.session_state.valores_registros:
        valores_registros = st.session_state.valores_registros
        
        # Primeira linha: Ativar e Entregar
        col1, col2 = st.columns(2)
        
        with col1:
            ativar_valor = "LIGADO (1)" if valores_registros["ativar"] else "DESLIGADO (0)"
            ativar_class = "modbus-true" if valores_registros["ativar"] else "modbus-false"
            st.markdown(f'''
            <div class="modbus-row">
                <div class="modbus-label">Ativar:</div>
                <div class="modbus-value {ativar_class}">{ativar_valor}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            entregar_valor = "LIGADO (1)" if valores_registros["entregar"] else "DESLIGADO (0)"
            entregar_class = "modbus-true" if valores_registros["entregar"] else "modbus-false"
            st.markdown(f'''
            <div class="modbus-row">
                <div class="modbus-label">Entregar:</div>
                <div class="modbus-value {entregar_class}">{entregar_valor}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        # Segunda linha: Gaveta e Posição Gaveta
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f'''
            <div class="modbus-row">
                <div class="modbus-label">Gaveta:</div>
                <div class="modbus-value modbus-number">{valores_registros["gaveta"]}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'''
            <div class="modbus-row">
                <div class="modbus-label">Pos. Gaveta:</div>
                <div class="modbus-value modbus-number">{valores_registros["posicao_gaveta"]}</div>
            </div>
            ''', unsafe_allow_html=True)
    else:
        # Exibir mensagem se o servidor estiver desconectado
        if not st.session_state.servidor_conectado:
            st.warning("Servidor Modbus desconectado. Verifique a conexão e reinicie a aplicação.")
    
    # Processar o clique no botão de atualização
    if refresh_button:
        # Usar os valores atuais de host e porta
        host = st.session_state.modbus_host
        port = st.session_state.modbus_port
        st.session_state.servidor_conectado = verificar_conexao_modbus(
            host=host,
            port=port
        )
        if st.session_state.servidor_conectado:
            st.session_state.valores_registros = ler_registros_modbus(
                host=host,
                port=port
            )
        st.rerun()
    
    # Adicionar seção para enviar novos valores para o servidor
    if st.session_state.servidor_conectado:
        # Adicionar espaço entre as seções
        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
        
        # Criar formulário para envio de novos valores
        with st.form(key="enviar_valores_form"):
            col1, col2 = st.columns(2)
            
            # Primeira linha: Ativar e Entregar (boolean)
            with col1:
                st.markdown('<p style="font-weight: bold; color: #000000; margin-bottom: 5px;">Novo valor para Ativar:</p>', unsafe_allow_html=True)
                novo_ativar = st.selectbox(
                    label="Novo valor para Ativar:",
                    options=["Selecione...", "LIGADO", "DESLIGADO"],
                    index=0,
                    key="novo_ativar_select",
                    label_visibility="collapsed"
                )
            
            with col2:
                st.markdown('<p style="font-weight: bold; color: #000000; margin-bottom: 5px;">Novo valor para Entregar:</p>', unsafe_allow_html=True)
                novo_entregar = st.selectbox(
                    label="Novo valor para Entregar:",
                    options=["Selecione...", "LIGADO", "DESLIGADO"],
                    index=0,
                    key="novo_entregar_select",
                    label_visibility="collapsed"
                )
            
            # Segunda linha: Gaveta e Posição Gaveta (numeric)
            with col1:
                st.markdown('<p style="font-weight: bold; color: #000000; margin-bottom: 5px;">Novo valor para Gaveta:</p>', unsafe_allow_html=True)
                novo_gaveta = st.number_input(
                    label="Novo valor para Gaveta:",
                    min_value=0,
                    max_value=100,
                    value=0,
                    key="novo_gaveta_input",
                    label_visibility="collapsed"
                )
            
            with col2:
                st.markdown('<p style="font-weight: bold; color: #000000; margin-bottom: 5px;">Novo valor para Pos. Gaveta:</p>', unsafe_allow_html=True)
                novo_posicao_gaveta = st.number_input(
                    label="Novo valor para Pos. Gaveta:",
                    min_value=0,
                    max_value=100,
                    value=0,
                    key="novo_posicao_gaveta_input",
                    label_visibility="collapsed"
                )
            
            # Botão para enviar os valores
            enviar_button = st.form_submit_button(
                label="Enviar novos dados para o servidor",
                type="primary"
            )
            
            # Processar o envio dos valores quando o botão for clicado
            if enviar_button:
                import subprocess
                import os
                
                # Preparar os argumentos para o comando
                cmd = ["python", os.path.join(os.getcwd(), "src/write_values.py")]
                
                # Adicionar host e porta atuais
                cmd.append("--host")
                cmd.append(st.session_state.modbus_host)
                cmd.append("--port")
                cmd.append(str(st.session_state.modbus_port))
                
                # Adicionar argumentos apenas para os campos que foram preenchidos
                if novo_ativar != "Selecione...":
                    cmd.append("--new-ativar")
                    cmd.append("true" if novo_ativar == "LIGADO" else "false")
                
                if novo_entregar != "Selecione...":
                    cmd.append("--new-entregar")
                    cmd.append("true" if novo_entregar == "LIGADO" else "false")
                
                if novo_gaveta > 0:
                    cmd.append("--new-gaveta")
                    cmd.append(str(novo_gaveta))
                
                if novo_posicao_gaveta > 0:
                    cmd.append("--new-posicao-gaveta")
                    cmd.append(str(novo_posicao_gaveta))
                
                # Executar o comando apenas se algum valor foi selecionado
                if len(cmd) > 2:
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        if result.returncode == 0:
                            st.success("Valores enviados com sucesso para o servidor!")
                            # Atualizar os valores exibidos
                            st.session_state.valores_registros = ler_registros_modbus(
                                host=st.session_state.modbus_host,
                                port=st.session_state.modbus_port
                            )
                            st.rerun()
                        else:
                            st.error(f"Erro ao enviar valores: {result.stderr}")
                    except Exception as e:
                        st.error(f"Erro ao executar o comando: {str(e)}")
                else:
                    st.warning("Nenhum valor foi selecionado para enviar.")
    
# Aplicar CSS personalizado
st.markdown("""
<style>
.connection-status {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
}
.connected {
    background-color: #4CAF50;
}
.disconnected {
    background-color: #F44336;
}
.modbus-row {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
}
.modbus-label {
    font-weight: bold;
    width: 120px;
    margin-right: 10px;
}
.modbus-value {
    padding: 10px 15px;
    border-radius: 4px;
    font-weight: bold;
    min-width: 100px;
    text-align: center;
}
.modbus-true {
    background-color: #e8f5e9;
    color: #2e7d32;
}
.modbus-false {
    background-color: #ffebee;
    color: #c62828;
}
.modbus-number {
    background-color: #e8f0fe;
    color: #1a73e8;
}
.refresh-button {
    background: none;
    border: none;
    color: #1a73e8;
    cursor: pointer;
    font-size: 20px;
    margin-left: 10px;
    padding: 0;
    vertical-align: middle;
}
.refresh-button:hover {
    color: #174ea6;
}
.status-container {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
}
button[kind="secondary"] {
    background-color: #FFB74D !important;
    color: white !important;
    border: none !important;
}
.border-container {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
    position: relative;
}
.container-title {
    position: absolute;
    top: -12px;
    left: 20px;
    background-color: white;
    padding: 0 10px;
    font-weight: 500;
    color: #555;
}

/* Estilos para os labels do formulário */
[data-testid="stForm"] label {
    font-weight: bold !important;
    color: #000000 !important;
}
</style>
""", unsafe_allow_html=True)
