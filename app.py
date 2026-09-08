from flask import Flask, request, jsonify, send_from_directory
import io
import wave
import matplotlib
import matplotlib.pyplot as plt
import linecoding as lc
matplotlib.use("Agg")

app = Flask(
    __name__,
    static_folder="static",
    static_url_path=""
)


@app.route("/")
def index():
    return app.send_static_file("index.html")

# --------------------------------------------------
# Plot signal
# --------------------------------------------------

def plot_signal(signal, bits, title):
    text_color = "#eaf7ff"
    waveform_color = "#48dded"

    fig, ax = plt.subplots(figsize=(12, 4))

    # -----------------------------
    # Build waveform coordinates
    # -----------------------------

    x = []
    y = []

    current_x = 0

    for bit_signal in signal:
        for level in bit_signal:
            x.append(current_x)
            y.append(level)
            current_x += 1

        if bit_signal:
            x.append(current_x)
            y.append(bit_signal[-1])

    signal_end = max(current_x, 1)

    # -----------------------------
    # Zero / TIME axis
    # -----------------------------

    ax.axhline(
        0,
        linewidth=1,
        color=text_color,
        alpha=0.4,
        zorder=1
    )

    # -----------------------------
    # Waveform
    # -----------------------------

    ax.step(
        x,
        y,
        where="post",
        linewidth=2,
        color=waveform_color,
        zorder=3
    )

    # -----------------------------
    # Bit boundaries + labels
    # -----------------------------

    position = 0

    for bit_signal, bit in zip(signal, bits):

        ax.axvline(
            position,
            linewidth=0.8,
            linestyle="--",
            color=text_color,
            alpha=0.18,
            zorder=0
        )

        midpoint = position + len(bit_signal) / 2

        ax.text(
            midpoint,
            1.25,
            bit,
            ha="center",
            va="bottom",
            fontsize=11,
            color=text_color
        )

        position += len(bit_signal)

    # Final bit boundary
    ax.axvline(
        signal_end,
        linewidth=0.8,
        linestyle="--",
        color=text_color,
        alpha=0.18,
        zorder=0
    )

    # -----------------------------
    # Amplitude ticks
    # -----------------------------

    ax.set_yticks([-1, 0, 1])

    ax.set_yticklabels(
        ["−V", "0", "+V"],
        color=text_color
    )

    ax.tick_params(
        axis="y",
        colors=text_color,
        length=5
    )

    # -----------------------------
    # Title
    # -----------------------------

    ax.set_title(
        title,
        color=text_color,
        pad=12
    )

    # -----------------------------
    # Plot limits
    # -----------------------------

    ax.set_xlim(0, signal_end)
    ax.set_ylim(-1.5, 1.6)

    ax.set_xticks([])
    ax.set_xlabel("")
    ax.set_ylabel("")

    # -----------------------------
    # Hide normal Matplotlib spines
    # -----------------------------

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)

    # -----------------------------
    # Horizontal amplitude grid
    # -----------------------------

    ax.grid(
        axis="y",
        linestyle="--",
        color=text_color,
        alpha=0.12
    )

    # -----------------------------
    # AMPLITUDE AXIS
    # -----------------------------

    amplitude_x = 0

    ax.annotate(
        "",
        xy=(amplitude_x, 1.45),
        xytext=(amplitude_x, -1.45),
        arrowprops=dict(
            arrowstyle="->",
            linewidth=1,
            color=text_color,
            shrinkA=0,
            shrinkB=0
        ),
        annotation_clip=False
    )

    ax.text(
        amplitude_x,
        1.55,
        "AMPLITUDE",
        color=text_color,
        ha="center",
        va="bottom",
        fontsize=9,
        clip_on=False
    )

    # -----------------------------
    # TIME AXIS
    # -----------------------------

    time_y = 0

    ax.annotate(
        "",
        xy=(signal_end, time_y),
        xytext=(0, time_y),
        arrowprops=dict(
            arrowstyle="->",
            linewidth=1,
            color=text_color,
            shrinkA=0,
            shrinkB=0
        ),
        annotation_clip=False
    )

    ax.text(
        signal_end,
        time_y - 0.08,
        "TIME",
        color=text_color,
        ha="right",
        va="top",
        fontsize=9,
        clip_on=False
    )

    # -----------------------------
    # Export SVG
    # -----------------------------

    fig.tight_layout()

    output = io.StringIO()

    fig.savefig(
        output,
        format="svg",
        bbox_inches="tight",
        transparent=True
    )

    plt.close(fig)

    return output.getvalue()


# --------------------------------------------------
# Scheme selection
# --------------------------------------------------

def encode_bits(bits, scheme):

    if scheme == "polar_nrz_l":
        return lc.nrz_l(bits), "Polar NRZ-L"

    elif scheme == "polar_nrz_i":
        return lc.nrz_i(bits), "Polar NRZ-I"

    elif scheme == "polar_rz":
        return lc.rz(bits), "Polar RZ"

    elif scheme == "manchester":
        return lc.manchester(bits), "Manchester"

    elif scheme == "differential_manchester":
        return lc.differential_manchester(bits), "Differential Manchester"

    else:
        raise ValueError("Invalid encoding scheme.")


# --------------------------------------------------
# Audio → bits
# --------------------------------------------------

def audio_to_bits(audio_file):

    # First implementation: PCM WAV.
    #
    # We decode the WAV container and use the actual
    # audio frame bytes rather than the WAV header.

    audio_file.seek(0)

    with wave.open(audio_file, "rb") as audio:

        frames = audio.readframes(audio.getnframes())

    bits = "".join(
        f"{byte:08b}"
        for byte in frames
    )

    return bits


# --------------------------------------------------
# API
# --------------------------------------------------

@app.route("/api/linecode", methods=["POST"])
def linecode():

    # ----------------------------------------------
    # BIT STRING MODE
    # ----------------------------------------------

    if request.is_json:

        data = request.get_json()

        if not data:
            return jsonify({
                "error": "No request data received."
            }), 400

        mode = data.get("mode")
        bits = data.get("bits")
        scheme = data.get("scheme")

        if mode != "bits":
            return jsonify({
                "error": "Invalid request mode."
            }), 400

        if not bits:
            return jsonify({
                "error": "Bit string is required."
            }), 400

        if not isinstance(bits, str):
            return jsonify({
                "error": "Bit string must be a string."
            }), 400

        if not all(bit in "01" for bit in bits):
            return jsonify({
                "error": "Bit string must contain only 0 and 1."
            }), 400

        if not scheme:
            return jsonify({
                "error": "Encoding scheme is required."
            }), 400

        try:
            signal, title = encode_bits(bits, scheme)

        except ValueError as error:
            return jsonify({
                "error": str(error)
            }), 400

        svg = plot_signal(
            signal,
            bits,
            title
        )

        return jsonify({
            "mode": "bits",
            "bits": bits,
            "scheme": scheme,
            "title": title,
            "svg": svg
        })

    # ----------------------------------------------
    # AUDIO MODE
    # ----------------------------------------------

    mode = request.form.get("mode")
    scheme = request.form.get("scheme")
    audio_file = request.files.get("audio")

    if mode != "audio":
        return jsonify({
            "error": "Invalid request mode."
        }), 400

    if not scheme:
        return jsonify({
            "error": "Encoding scheme is required."
        }), 400

    if audio_file is None:
        return jsonify({
            "error": "Audio file is required."
        }), 400

    try:
        bits = audio_to_bits(audio_file)

    except Exception as error:
        return jsonify({
            "error": f"Could not process audio file: {error}"
        }), 400

    if not bits:
        return jsonify({
            "error": "Audio file contains no data."
        }), 400

    try:
        signal, title = encode_bits(bits, scheme)

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    svg = plot_signal(
        signal,
        bits,
        title
    )

    return jsonify({
        "mode": "audio",
        "bits": bits,
        "bit_count": len(bits),
        "scheme": scheme,
        "title": title,
        "svg": svg
    })


# --------------------------------------------------
# Run
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        debug=True
    )