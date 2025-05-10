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

def save_photos(api, download_dir="./downloaded_photos", limit=10):
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