import logging
import re

logger = logging.getLogger("analyzer.parser.config_analyzer")

class ConfigAnalyzer:
    """설정 파일 분석 클래스"""
    
    def analyze(self, config_files):
        """설정 파일 분석"""
        config_info = {}
        
        for file_info in config_files:
            path = file_info['path']
            content = file_info['content']
            
            # 파일 유형에 따라 분석 메서드 선택
            if path.endswith(('.yml', '.yaml')):
                yml_config = self.analyze_yml_file(content)
                config_info.update(yml_config)
            elif path.endswith('.properties'):
                prop_config = self.analyze_properties_file(content)
                config_info.update(prop_config)
        
        return config_info
    
    def analyze_yml_file(self, content):
        """YAML 설정 파일 분석"""
        config_info = {}
        
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
            
        return config_info
    
    def analyze_properties_file(self, content):
        """Properties 설정 파일 분석"""
        config_info = {}
        
        # 프로퍼티 파일 파싱
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split('=', 1)
                if len(parts) == 2:
                    key, value = parts
                    config_info[key.strip()] = value.strip()
                    
        return config_info