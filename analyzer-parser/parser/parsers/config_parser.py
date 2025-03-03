"""
애플리케이션 구성 파일을 분석하기 위한 모듈
"""
import re

def analyze_config_file(path, content):
    """
    애플리케이션 구성 파일(properties/yml) 분석
    """
    config_info = {}
    
    if path.endswith(('.yml', '.yaml')):
        # 주요 구성을 위한 기본 YAML 파싱
        server_port_match = re.search(r'server:\s*\n\s*port:\s*(\d+)', content)
        if server_port_match:
            config_info['server.port'] = server_port_match.group(1)
        
        datasource_match = re.search(r'datasource:\s*\n\s*url:\s*([^\n]+)', content)
        if datasource_match:
            config_info['spring.datasource.url'] = datasource_match.group(1).strip()
        
        jpa_ddl_match = re.search(r'jpa:\s*\n(?:[^\n]+\n)*\s*hibernate:\s*\n(?:[^\n]+\n)*\s*ddl-auto:\s*([^\n]+)', content)
        if jpa_ddl_match:
            config_info['spring.jpa.hibernate.ddl-auto'] = jpa_ddl_match.group(1).strip()
    
    elif path.endswith('.properties'):
        # 프로퍼티 파일 파싱
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split('=', 1)
                if len(parts) == 2:
                    key, value = parts
                    config_info[key.strip()] = value.strip()
    
    return config_info