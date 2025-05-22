#!/usr/bin/env python3
import argparse
import getpass
import sys
import os
from datetime import datetime, timedelta, timezone
from iCloudPhotoManager import authenticate_icloud, download_photos_by_date, get_photos_by_date_range, get_photos_info, parse_date

def main():
    # 명령행 인자 파싱
    parser = argparse.ArgumentParser(description='iCloud Photos에서 특정 날짜 범위의 사진과 동영상을 다운로드합니다.')
    
    # 필수 인자
    parser.add_argument('--username', '-u', required=True, help='iCloud 이메일 주소')
    parser.add_argument('--start-date', '-s', required=True, help='시작 날짜 (YYYY-MM-DD 또는 YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--end-date', '-e', required=True, help='종료 날짜 (YYYY-MM-DD 또는 YYYY-MM-DD HH:MM:SS)')
    
    # 선택적 인자
    parser.add_argument('--password', '-p', help='iCloud 비밀번호 (입력하지 않으면 프롬프트 표시)')
    parser.add_argument('--download-dir', '-d', default='./downloaded_photos', help='다운로드 디렉토리 (기본값: ./downloaded_photos)')
    parser.add_argument('--max-downloads', '-m', type=int, help='최대 다운로드 개수')
    parser.add_argument('--list-only', '-l', action='store_true', help='다운로드 없이 목록만 표시')
    parser.add_argument('--quiet', '-q', action='store_true', help='상세 출력 생략 (간소화된 출력)')
    
    args = parser.parse_args()

    # iCloud에 인증
    api = authenticate_icloud(args.username, args.password)

    start_date = parse_date(args.start_date)
    end_date = parse_date(args.end_date)
    #print(f"start_date: {start_date}, end_date: {end_date}")
    download_dir = args.download_dir
    # print(f"download_dir: {download_dir}")

    # 종료 날짜는 해당 일의 마지막 시간으로 설정 (시간이 지정되지 않은 경우)
    if ' ' not in args.end_date:
        end_date = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59, tzinfo=timezone.utc) + timedelta(days=1)
    
    print(f"\n{start_date.strftime('%Y-%m-%d %H:%M:%S')}부터 {end_date.strftime('%Y-%m-%d %H:%M:%S')}까지의 미디어를 검색합니다...\n")
    
    # 날짜 범위 내의 사진 가져오기
    filtered_photos = get_photos_by_date_range(api, start_date, end_date, download_dir = download_dir)
    
    if not filtered_photos:
        print("지정된 날짜 범위 내에 미디어가 없습니다.")
        return
    
    # 사진 정보 가져오기
    # photos_info = get_photos_info(filtered_photos)
    
    # # 사진 정보 출력
    # if not args.quiet:
    #     print("\n검색된 미디어 목록:")
    #     for i, photo in enumerate(photos_info, 1):
    #         print(f"{i}. [{photo['type']}] {photo['filename']} - 생성일: {photo['created']}, 크기: {photo['dimensions']}, 용량: {photo['size_kb']}KB")
    # else:
    #     print(f"검색된 미디어 개수: {len(photos_info)}")
    
    # # 다운로드 여부 확인
    # if args.list_only:
    #     get_photos_by_date_range(api, start_date, end_date)
    # else:
    #     if not args.quiet:
    #         download = input("\n이 미디어들을 다운로드하시겠습니까? (y/n): ").lower()
    #         if download == 'y':
    #             download_photos_by_date(api, args.download_dir, start_date, end_date, args.max_downloads, args.quiet)

if __name__ == "__main__":
    # 필요한 패키지 확인
    try:
        import pyicloud
    except ImportError:
        print("pyicloud 패키지가 설치되어 있지 않습니다.")
        print("설치하려면 다음 명령어를 실행하세요: pip install pyicloud")
        sys.exit(1)
        
    main()