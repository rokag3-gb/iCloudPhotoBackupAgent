#!/usr/bin/env python3
import getpass
import sys
from pyicloud import PyiCloudService

def authenticate_icloud():
    """iCloud에 인증하고 PyiCloudService 객체를 반환합니다."""
    username = input("iCloud 이메일 주소를 입력하세요: ")
    password = getpass.getpass("iCloud 비밀번호를 입력하세요: ")
    
    try:
        api = PyiCloudService(username, password)
    except Exception as e:
        print(f"로그인 실패: {e}")
        sys.exit(1)
    
    # 2단계 인증이 필요한 경우
    if api.requires_2fa:
        print("2단계 인증이 필요합니다.")
        code = input("인증 코드를 입력하세요: ")
        result = api.validate_2fa_code(code)
        print(f"2단계 인증 결과: {result}")
        
        if not result:
            print("잘못된 인증 코드입니다.")
            sys.exit(1)
    
    # 앱별 비밀번호가 필요한 경우
    if api.requires_2sa:
        print("앱별 비밀번호가 필요합니다. iCloud 계정 설정에서 앱별 비밀번호를 생성해 사용하세요.")
        sys.exit(1)
        
    return api

def get_photos_count(api):
    """사진 라이브러리의 전체 사진 수를 반환합니다."""
    try:
        # photos 속성에 접근하여 모든 사진 얻기
        all_photos = api.photos.all
        photo_count = len(all_photos)
        return photo_count
    except Exception as e:
        print(f"사진 수를 가져오는 중 오류 발생: {e}")
        return 0

def get_photos_list(api, limit=100):
    """
    사진 라이브러리에서 사진 목록을 가져옵니다.
    limit: 가져올 최대 사진 수 (기본값: 100)
    """
    photos_info = []
    
    try:
        all_photos = api.photos.all
        count = 0
        
        for photo in all_photos:
            if count >= limit:
                break
                
            # 각 사진에 대한 정보 수집
            photo_info = {
                'filename': photo.filename,
                'created': photo.created.strftime('%Y-%m-%d %H:%M:%S'),
                'dimensions': f"{photo.width}x{photo.height}",
                'size_kb': round(photo.size / 1024, 2)
            }
            photos_info.append(photo_info)
            count += 1
            
        return photos_info
    except Exception as e:
        print(f"사진 목록을 가져오는 중 오류 발생: {e}")
        return []

def get_photos_by_date_range(api, start_date, end_date):
    """
    특정 날짜 범위 내의 사진과 동영상을 필터링합니다.
    
    :param api: PyiCloudService 객체
    :param start_date: 시작 날짜 (datetime 객체)
    :param end_date: 종료 날짜 (datetime 객체)
    :return: 필터링된 사진 목록
    """
    filtered_photos = []
    
    try:
        # 모든 사진 가져오기
        all_photos = api.photos.all
        print(f"총 {len(all_photos)}개의 미디어를 확인 중...")
        
        # 진행 상황 표시를 위한 변수
        total = len(all_photos)
        processed = 0
        
        for photo in all_photos:
            processed += 1
            if processed % 100 == 0:
                print(f"진행 중: {processed}/{total} 확인 중...")
            
            # 사진 생성 날짜 확인
            created_date = photo.created
            
            # 지정된 날짜 범위 내에 있는지 확인
            if start_date <= created_date <= end_date:
                filtered_photos.append(photo)
        
        print(f"날짜 범위 내 미디어 수: {len(filtered_photos)}")
        return filtered_photos
    
    except Exception as e:
        print(f"사진 필터링 중 오류 발생: {e}")
        return []

def get_photos_info(photos_list):
    """
    사진 목록에서 각 사진의 정보를 추출합니다.
    
    :param photos_list: 사진 객체 목록
    :return: 사진 정보 딕셔너리 목록
    """
    photos_info = []
    
    for photo in photos_list:
        # 각 사진에 대한 정보 수집
        media_type = "비디오" if photo.item_type == "movie" else "사진"
        
        photo_info = {
            'filename': photo.filename,
            'created': photo.created.strftime('%Y-%m-%d %H:%M:%S'),
            'dimensions': f"{photo.width}x{photo.height}" if hasattr(photo, 'width') and hasattr(photo, 'height') else "정보 없음",
            'size_kb': round(photo.size / 1024, 2) if hasattr(photo, 'size') else 0,
            'type': media_type
        }
        photos_info.append(photo_info)
    
    return photos_info

def download_photos_by_date(api, download_dir="./downloaded_photos", start_date=None, end_date=None):
    """
    특정 날짜 범위 내의 사진을 다운로드합니다.
    
    :param api: PyiCloudService 객체
    :param download_dir: 다운로드할 디렉토리
    :param start_date: 시작 날짜 (datetime 객체)
    :param end_date: 종료 날짜 (datetime 객체)
    """
    # 날짜 범위 내의 사진 가져오기
    filtered_photos = get_photos_by_date_range(api, start_date, end_date)
    
    if not filtered_photos:
        print("지정된 날짜 범위 내에 다운로드할 미디어가 없습니다.")
        return
    
    # 다운로드 디렉토리가 없으면 생성
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    # 다운로드 진행
    download_count = int(input(f"총 {len(filtered_photos)}개의 미디어가 발견되었습니다. 몇 개를 다운로드하시겠습니까? (전체: {len(filtered_photos)}): "))
    download_count = min(download_count, len(filtered_photos))
    
    print(f"{download_count}개의 미디어를 다운로드합니다...")
    
    count = 0
    for photo in filtered_photos[:download_count]:
        try:
            # 파일명이 중복되지 않도록 날짜를 접두사로 추가
            date_prefix = photo.created.strftime('%Y%m%d_%H%M%S_')
            filename = os.path.join(download_dir, date_prefix + photo.filename)
            
            print(f"다운로드 중: {photo.filename}")
            with open(filename, 'wb') as f:
                f.write(photo.download().raw.read())
                
            print(f"다운로드 완료: {filename}")
            count += 1
        except Exception as e:
            print(f"'{photo.filename}' 다운로드 중 오류 발생: {e}")
    
    print(f"총 {count}개의 미디어를 다운로드했습니다.")

def parse_date(date_str):
    """문자열 형태의 날짜를 datetime 객체로 변환합니다."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            print(f"잘못된 날짜 형식입니다: {date_str}")
            print("올바른 형식: 'YYYY-MM-DD' 또는 'YYYY-MM-DD HH:MM:SS'")
            sys.exit(1)

def download_photos(api, download_dir="./downloaded_photos", limit=10):
    """
    사진을 로컬 디렉토리에 다운로드합니다.
    download_dir: 다운로드할 디렉토리 (기본값: ./downloaded_photos)
    limit: 다운로드할 최대 사진 수 (기본값: 10)
    """
    import os
    
    # 다운로드 디렉토리가 없으면 생성
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    try:
        all_photos = api.photos.all
        count = 0
        
        for photo in all_photos:
            if count >= limit:
                break
                
            # 사진 다운로드
            filename = os.path.join(download_dir, photo.filename)
            with open(filename, 'wb') as f:
                f.write(photo.download().raw.read())
                
            print(f"다운로드 완료: {photo.filename}")
            count += 1
            
        print(f"총 {count}개의 사진을 다운로드했습니다.")
    except Exception as e:
        print(f"사진 다운로드 중 오류 발생: {e}")