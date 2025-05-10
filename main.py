from iCloudPhotoManager import authenticate_icloud, get_photos_count, get_photos_list, save_photos

def main():
    # iCloud에 인증
    api = authenticate_icloud()
    
    # 전체 사진 수 가져오기
    total_photos = get_photos_count(api)
    print(f"iCloud Photos에 총 {total_photos}개의 사진이 있습니다.")
    
    # 사진 목록 가져오기 (기본값: 최대 100개)
    photos_list = get_photos_list(api)
    
    # 사진 정보 출력
    print("\n사진 목록:")
    for i, photo in enumerate(photos_list, 1):
        print(f"{i}. {photo['filename']} - 생성일: {photo['created']}, 크기: {photo['dimensions']}, 용량: {photo['size_kb']}KB")
    
    # 사진 다운로드 여부 묻기
    download = input("\n사진을 다운로드하시겠습니까? (y/n): ").lower()
    if download == 'y':
        limit = int(input("다운로드할 사진 수를 입력하세요: "))
        save_photos(api, limit=limit)

if __name__ == "__main__":
    # 필요한 패키지 확인
    try:
        import pyicloud
    except ImportError:
        print("pyicloud 패키지가 설치되어 있지 않습니다.")
        print("설치하려면 다음 명령어를 실행하세요: pip install pyicloud")
        sys.exit(1)
        
    main()