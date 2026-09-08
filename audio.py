import wave
import numpy as np


def audio_to_energy_bits(audio_file, chunk_count):

    audio_file.seek(0)

    try:
        with wave.open(audio_file, "rb") as audio:
            if audio.getcomptype() != "NONE":
                raise ValueError("Only uncompressed PCM WAV files are supported.")

            frame_count = audio.getnframes()
            channel_count = audio.getnchannels()
            sample_width = audio.getsampwidth()

            bits_per_frame = channel_count * sample_width * 8
            frames = audio.readframes(frame_count)
    except (EOFError, wave.Error) as error:
        raise ValueError("Audio must be a valid WAV file.") from error

    if sample_width not in (1, 2, 3, 4):
        raise ValueError(
            f"Unsupported PCM sample width: {sample_width * 8} bits"
        )

    if not frames:
        return "", 0

    raw_samples = np.frombuffer(frames, dtype=np.uint8)

    if sample_width == 1:
        samples = raw_samples.astype(np.float32) - 128
    elif sample_width == 3:
        sample_values = raw_samples.reshape(-1, 3).astype(np.int32)
        samples = sample_values[:, 0] | sample_values[:, 1] << 8 | sample_values[:, 2] << 16
        samples = np.where(samples & 0x800000, samples - 0x1000000, samples)
    else:
        sample_dtype = np.dtype(f"<i{sample_width}")
        samples = raw_samples.view(sample_dtype)

    samples = samples.reshape(-1, channel_count).mean(axis=1)
    chunk_count = min(chunk_count, len(samples))
    chunk_edges = np.linspace(0, len(samples), chunk_count + 1, dtype=int)
    chunk_energy = np.array([
        np.sqrt(np.mean(samples[start:end] ** 2)) if end > start else 0.0
        for start, end in zip(chunk_edges[:-1], chunk_edges[1:])
    ])

    energy_threshold = np.median(chunk_energy)
    bits = np.where(chunk_energy > energy_threshold, "1", "0")
    return "".join(bits), frame_count * bits_per_frame