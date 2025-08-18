#!/usr/bin/env python3
"""
Warpage Analyzer - 명령행 인터페이스 진입점
Warpage Analyzer - CLI Entry Point

다양한 해상도의 워페이지 데이터를 분석하는 모듈식 도구
더 나은 유지보수를 위해 단일 파일 구조에서 모듈 설계로 리팩토링
A modular tool for analyzing warpage data across different resolutions
Refactored from single-file architecture to modular design for better maintainability.

사용법 / Usage:
    python cli_interface.py [options]                  # 명령행 모드 / Command line mode
    python cli_interface.py --interactive              # 대화식 모드 / Interactive mode
    python cli_interface.py --help                     # 도움말 표시 / Show help
    
예시 / Example:
    python cli_interface.py --cmap=plasma --vmin=-1500 --vmax=-800 --show
"""

import sys
from cli import parse_command_line_args, interactive_mode
from analyzer import analyze_warpage


def main():
    """
    Warpage Analyzer 애플리케이션의 메인 진입점
    Main entry point for the Warpage Analyzer application.
    
    명령행 인수를 처리하고 분석을 실행
    Handles command line arguments and runs the analysis.
    """
    # 대화식 모드 플래그 확인 / Check for interactive mode flag
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        config = interactive_mode()
    else:
        # 명령행 인수 파싱 / Parse command line arguments
        config = parse_command_line_args()
    
    # 분석 실행 / Run analysis
    analyze_warpage(config)


if __name__ == "__main__":
    main() 