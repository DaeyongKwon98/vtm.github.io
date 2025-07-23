import os
import ffmpeg

# 경로 설정
base_path = "/home/daeyong/gaudio_retrieval_evaluation/vtm_demo"
audio_root = os.path.join(base_path, "audios")
video_root = os.path.join(base_path, "videos")
output_root = os.path.join(base_path, "mixed")

# 비디오 ID 목록 (audios 하위 디렉토리명 기준)
video_ids = sorted([d for d in os.listdir(audio_root) if os.path.isdir(os.path.join(audio_root, d))])

for video_id in video_ids:
    print(f"\n🎬 처리 중: video_id = {video_id}")

    video_path = os.path.join(video_root, f"{video_id}.mp4")
    audio_dir = os.path.join(audio_root, video_id)
    output_dir = os.path.join(output_root, video_id)
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(video_path):
        print(f"  ⛔ 비디오 파일 없음: {video_path}")
        continue

    # 3개의 오디오(wav) 순회
    for i in range(1, 4):
        # e.g., *_1.wav, *_2.wav, *_3.wav 찾기
        audio_candidates = [f for f in os.listdir(audio_dir) if f.endswith(f"_{i}.wav")]
        if not audio_candidates:
            print(f"  ⚠️ 오디오 파일 없음: {audio_dir}/*_{i}.wav")
            continue

        audio_path = os.path.join(audio_dir, audio_candidates[0])
        output_path = os.path.join(output_dir, f"mixed_{i}.mp4")

        try:
            print(f"  ▶️ 믹싱: {video_path} + {audio_path} → {output_path}")

            # 영상 입력
            input_video = ffmpeg.input(video_path)
            input_audio = ffmpeg.input(audio_path)

            # 오디오 믹스 (비디오 오디오 + 배경 음악)
            # 필요 시 배경음 볼륨 조절 (e.g., 2.5배)
            bg_audio = input_audio.audio.filter('volume', 1.0)

            mixed_audio = ffmpeg.filter(
                [input_video.audio, bg_audio],
                'amix',
                inputs=2,
                dropout_transition=0
            )

            # 최종 출력 구성
            (
                ffmpeg
                .output(
                    input_video.video,  # 비디오 그대로
                    mixed_audio,        # 믹스된 오디오
                    output_path,
                    vcodec='copy',
                    acodec='aac',
                    shortest=None
                )
                .overwrite_output()
                .run(quiet=True)
            )

            print(f"  ✅ 완료: {output_path}")

        except ffmpeg.Error as e:
            print(f"  ⛔️ 오류 발생: {audio_path}")
            print(e.stderr.decode())
