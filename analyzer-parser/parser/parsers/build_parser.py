"""
빌드 파일(Gradle/Maven)을 파싱하기 위한 모듈
"""
import re

def parse_gradle_file(content):
    """
    build.gradle 파일에서 프로젝트 정보 추출
    """
    info = {
        'plugins': [],
        'dependencies': [],
        'springBootVersion': '',
        'javaVersion': '',
        'group': '',
        'version': ''
    }
    
    # 플러그인 추출
    plugin_pattern = r"id ['\"](.*?)['\"]( version ['\"](.*?)['\"])?"
    plugins = re.finditer(plugin_pattern, content)
    for plugin in plugins:
        plugin_info = f"{plugin.group(1)}"
        if plugin.group(3):  # 버전이 있는 경우
            plugin_info += f" {plugin.group(3)}"
        info['plugins'].append(plugin_info)
    
    # 의존성 추출
    dep_pattern = r"(implementation|compileOnly|runtimeOnly|annotationProcessor) ['\"](.*?)['\"]"
    dependencies = re.finditer(dep_pattern, content)
    for dep in dependencies:
        info['dependencies'].append(f"{dep.group(1)}: {dep.group(2)}")
    
    # Spring Boot 버전 추출
    spring_boot_pattern = r"(?:org\.springframework\.boot['\"] version ['\"]|id\(['\"]org\.springframework\.boot['\"](?:\) version ['\"])|id\s*=\s*['\"]*org\.springframework\.boot['\"]*(?:\s*version\s*=\s*['\"]))(.*?)['\"]"
    spring_boot_match = re.search(spring_boot_pattern, content)
    if spring_boot_match:
        info['springBootVersion'] = spring_boot_match.group(1)
    
    # Java 버전 추출
    java_version_pattern = r"JavaLanguageVersion\.of\((\d+)\)"
    java_match = re.search(java_version_pattern, content)
    if java_match:
        info['javaVersion'] = java_match.group(1)
    
    # 그룹 및 버전 추출
    group_pattern = r"group = ['\"](.*?)['\"]"
    version_pattern = r"version = ['\"](.*?)['\"]"
    
    group_match = re.search(group_pattern, content)
    version_match = re.search(version_pattern, content)
    
    if group_match:
        info['group'] = group_match.group(1)
    if version_match:
        info['version'] = version_match.group(1)
    
    return info

def parse_maven_file(content):
    """
    pom.xml 파일에서 프로젝트 정보 추출
    """
    info = {
        'plugins': [],
        'dependencies': [],
        'springBootVersion': '',
        'javaVersion': '',
        'group': '',
        'version': ''
    }
    
    # 그룹 및 아티팩트 추출
    group_pattern = r"<groupId>(.*?)</groupId>"
    version_pattern = r"<version>(.*?)</version>"
    artifact_pattern = r"<artifactId>(.*?)</artifactId>"
    
    # parent 태그 내부가 아닌 첫 번째 group, version, artifact 가져오기
    content_no_parent = re.sub(r"<parent>.*?</parent>", "", content, flags=re.DOTALL)
    
    group_match = re.search(group_pattern, content_no_parent)
    version_match = re.search(version_pattern, content_no_parent)
    artifact_match = re.search(artifact_pattern, content_no_parent)
    
    if group_match:
        info['group'] = group_match.group(1)
    if version_match:
        info['version'] = version_match.group(1)
    if artifact_match:
        info['artifactId'] = artifact_match.group(1)
    
    # 의존성 추출
    dep_pattern = r"<dependency>\s*<groupId>(.*?)</groupId>\s*<artifactId>(.*?)</artifactId>\s*(?:<version>(.*?)</version>)?"
    dependencies = re.finditer(dep_pattern, content, re.DOTALL)
    for dep in dependencies:
        groupId = dep.group(1)
        artifactId = dep.group(2)
        version = dep.group(3) if dep.group(3) else "managed"
        info['dependencies'].append(f"{groupId}:{artifactId}:{version}")
    
    # Spring Boot 버전 추출
    spring_boot_pattern = r"<parent>\s*<groupId>org\.springframework\.boot</groupId>\s*<artifactId>spring-boot-starter-parent</artifactId>\s*<version>(.*?)</version>"
    spring_boot_match = re.search(spring_boot_pattern, content, re.DOTALL)
    if spring_boot_match:
        info['springBootVersion'] = spring_boot_match.group(1)
    
    # Java 버전 추출
    java_version_pattern = r"<java.version>(.*?)</java.version>"
    java_match = re.search(java_version_pattern, content)
    if java_match:
        info['javaVersion'] = java_match.group(1)
    
    # 플러그인 추출
    plugin_pattern = r"<plugin>\s*<groupId>(.*?)</groupId>\s*<artifactId>(.*?)</artifactId>\s*(?:<version>(.*?)</version>)?"
    plugins = re.finditer(plugin_pattern, content, re.DOTALL)
    for plugin in plugins:
        groupId = plugin.group(1)
        artifactId = plugin.group(2)
        version = plugin.group(3) if plugin.group(3) else "managed"
        info['plugins'].append(f"{groupId}:{artifactId}:{version}")
    
    return info