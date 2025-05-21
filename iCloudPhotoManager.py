#!/usr/bin/env python3
import getpass
import sys
import os
from datetime import datetime, timezone, timedelta
from pyicloud import PyiCloudService
from pyicloud.services.photos import PhotoAsset

def authenticate_icloud(username: str, password: str = None):
    """iCloud에 인증하고 PyiCloudService 객체를 반환합니다."""
    #username = input("iCloud 이메일 주소를 입력하세요: ")
    #password = getpass.getpass("iCloud 비밀번호를 입력하세요: ")
    if not password:
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

def get_photos_count(api: PyiCloudService):
    """사진 라이브러리의 전체 사진 수를 반환합니다."""
    try:
        # photos 속성에 접근하여 모든 사진 얻기
        all_photos = api.photos.all
        photo_count = len(all_photos)
        return photo_count
    except Exception as e:
        print(f"사진 수를 가져오는 중 오류 발생: {e}")
        return 0

def get_photos_list(api: PyiCloudService, limit: int = 100):
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

def get_photos_by_date_range(api: PyiCloudService, start_date: datetime, end_date: datetime, limit: int = 10, download_dir: str = "./downloaded_photos"):
    """
    특정 날짜 범위 내의 사진과 동영상을 필터링합니다.
    
    :param api: PyiCloudService 객체
    :param start_date: 시작 날짜 (datetime 객체)
    :param end_date: 종료 날짜 (datetime 객체)
    :param limit: 최대 처리할 사진 수
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

            # iCloud의 시간을 UTC로 변환하고 KST로 변환
            # datetime_created: datetime = photo.created.astimezone(timezone.utc)
            # datetime_created: datetime = photo.created.astimezone(timezone.utc).replace(tzinfo=timezone.utc) + timedelta(hours=9)
            datetime_created: datetime = photo.created.astimezone(timezone.utc) + timedelta(hours = 9)
            
            # print(f"datetime_created: {datetime_created}")
            # print(f"start_date: {start_date}")
            # print(f"end_date: {end_date}")
            # print(f"start_date <= datetime_created: {start_date <= datetime_created}")
            # print(f"datetime_created <= end_date: {datetime_created <= end_date}")

            # 사진 생성 날짜가 지정된 날짜 범위 내에 있는지 확인
            if start_date <= datetime_created < end_date:
                filtered_photos.append(photo)
                download_photo(photo, download_dir)
                # print_photo_info(photo)
                # if processed >= limit:
                #     break

        print(f"날짜 범위 내 미디어 수: {len(filtered_photos)}")
        return filtered_photos
    
    except Exception as e:
        print(f"사진 필터링 중 오류 발생: {e}")
        return []

def print_photo_info(photo):
    """
    사진 목록에서 각 사진의 정보를 추출합니다.
    
    :param photos_list: 사진 객체 목록
    :return: 사진 정보 딕셔너리 목록
    """
    # photos_info = []
    
    # 미디어 타입별 확장자 정의
    photo_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.heic', '.heif', '.tiff', '.webp'}
    video_extensions = {'.mp4', '.mov', '.avi', '.wmv', '.flv', '.mkv', '.m4v', '.3gp'}
    
    # 파일 확장자 추출 (소문자로 변환)
    file_extension = os.path.splitext(photo.filename.lower())[1]
    
    # 확장자 기반으로 미디어 타입 판단
    if file_extension in photo_extensions:
        type = "사진"
    elif file_extension in video_extensions:
        type = "비디오"
    else:
        type = "알 수 없음"
        print(f"알 수 없는 파일 형식: {photo.filename}")
    # datetime_created: datetime = photo.created.astimezone(timezone.utc) + timedelta(hours = 9)
    photo_info = {
        'filename': photo.filename,
        # 'created': photo.created.strftime('%Y-%m-%d %H:%M:%S'),
        'created': photo.created.astimezone(timezone.utc) + timedelta(hours = 9),
        'dimensions': f"{photo.width}x{photo.height}" if hasattr(photo, 'width') and hasattr(photo, 'height') else "정보 없음",
        'size_kb': round(photo.size / 1024, 2) if hasattr(photo, 'size') else 0,
        'type': type
    }

    print("\n검색된 미디어 목록:")
    # for i, photo in enumerate(photo_info, 1):
    print(f"[{photo_info['type']}] {photo_info['filename']} - 생성일: {photo_info['created']}, 크기: {photo_info['dimensions']}, 용량: {photo_info['size_kb']}KB")
    # photos_info.append(photo_info)
    # return photos_info

def get_photos_info(photos_list):
    """
    사진 목록에서 각 사진의 정보를 추출합니다.
    
    :param photos_list: 사진 객체 목록
    :return: 사진 정보 딕셔너리 목록
    """
    photos_info = []
    
    # 미디어 타입별 확장자 정의
    photo_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.heic', '.heif', '.tiff', '.webp'}
    video_extensions = {'.mp4', '.mov', '.avi', '.wmv', '.flv', '.mkv', '.m4v', '.3gp'}
    
    for photo in photos_list:

        # 각 사진의 모든 속성 출력
        # print("\n사진 객체의 모든 속성:")
        # for attr in dir(photo):
        #     if not attr.startswith('_'):  # 내부 속성 제외
        #         try:
        #             value = getattr(photo, attr)
        #             print(f"{attr}: {value}")
        #         except:
        #             pass

        # 각 사진에 대한 정보 수집
        # type = "비디오" if photo.item_type == "movie" else "사진"

        # 파일 확장자 추출 (소문자로 변환)
        file_extension = os.path.splitext(photo.filename.lower())[1]
        
        # 확장자 기반으로 미디어 타입 판단
        if file_extension in photo_extensions:
            type = "사진"
        elif file_extension in video_extensions:
            type = "비디오"
        else:
            type = "알 수 없음"
            print(f"알 수 없는 파일 형식: {photo.filename}")
        
        photo_info = {
            'filename': photo.filename,
            'created': photo.created.strftime('%Y-%m-%d %H:%M:%S'),
            'dimensions': f"{photo.width}x{photo.height}" if hasattr(photo, 'width') and hasattr(photo, 'height') else "정보 없음",
            'size_kb': round(photo.size / 1024, 2) if hasattr(photo, 'size') else 0,
            'type': type
        }
        photos_info.append(photo_info)
    
    return photos_info

def download_photos_by_date(api, download_dir="./downloaded_photos", start_date=None, end_date=None, limit: int = 10):
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
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            return dt.replace(tzinfo=timezone.utc)
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

def download_photo(photo: PhotoAsset, download_dir="./downloaded_photos"):
    """
    단일 사진을 로컬 디렉토리에 다운로드합니다.
    
    :param photo: PhotoAsset 객체
    :param download_dir: 다운로드할 디렉토리 (기본값: ./downloaded_photos)
    :return: 다운로드된 파일의 전체 경로
    """
    # 다운로드 디렉토리가 없으면 생성
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    try:
        # 파일명이 중복되지 않도록 날짜를 접두사로 추가
        date_prefix = (photo.created.astimezone(timezone.utc) + timedelta(hours=9)).strftime('%Y%m%d_%H%M%S_')
        filename = os.path.join(download_dir, date_prefix + photo.filename)
        
        print(f"다운로드 중: {photo.filename}")
        with open(filename, 'wb') as f:
            f.write(photo.download().raw.read())
            
        print(f"다운로드 완료: {filename}")
        return filename
    except Exception as e:
        print(f"'{photo.filename}' 다운로드 중 오류 발생: {e}")
        return None