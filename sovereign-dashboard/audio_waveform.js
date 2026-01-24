/**
 * 🎵 AUDIO WAVEFORM VISUALIZATION
 * ================================
 * Real-time audio waveform display for podcast panel
 */

class AudioWaveform {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error(`Canvas ${canvasId} not found`);
            return;
        }

        this.ctx = this.canvas.getContext('2d');
        this.audioContext = null;
        this.analyser = null;
        this.dataArray = null;
        this.animationId = null;

        // Styling
        this.waveColor = '#00ff88';
        this.backgroundColor = 'rgba(0, 0, 0, 0.1)';
        this.lineWidth = 2;

        this.setupCanvas();
    }

    setupCanvas() {
        // Set canvas size
        this.canvas.width = this.canvas.offsetWidth;
        this.canvas.height = this.canvas.offsetHeight;

        // Handle resize
        window.addEventListener('resize', () => {
            this.canvas.width = this.canvas.offsetWidth;
            this.canvas.height = this.canvas.offsetHeight;
        });
    }

    async connectAudioElement(audioElement) {
        /**
         * Connect to an HTML audio element for visualization
         */
        try {
            if (!this.audioContext) {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            }

            // Create analyser
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 2048;

            const bufferLength = this.analyser.frequencyBinCount;
            this.dataArray = new Uint8Array(bufferLength);

            // Connect audio element
            const source = this.audioContext.createMediaElementSource(audioElement);
            source.connect(this.analyser);
            this.analyser.connect(this.audioContext.destination);

            // Start visualization
            this.startVisualization();

        } catch (error) {
            console.error('Audio connection failed:', error);
        }
    }

    async connectMicrophone() {
        /**
         * Connect to microphone for live input visualization
         */
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            if (!this.audioContext) {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            }

            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 2048;

            const bufferLength = this.analyser.frequencyBinCount;
            this.dataArray = new Uint8Array(bufferLength);

            const source = this.audioContext.createMediaStreamSource(stream);
            source.connect(this.analyser);

            this.startVisualization();

        } catch (error) {
            console.error('Microphone access failed:', error);
        }
    }

    startVisualization() {
        /**
         * Start the waveform animation loop
         */
        const draw = () => {
            this.animationId = requestAnimationFrame(draw);

            if (!this.analyser || !this.dataArray) return;

            this.analyser.getByteTimeDomainData(this.dataArray);

            // Clear canvas
            this.ctx.fillStyle = this.backgroundColor;
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

            // Draw waveform
            this.ctx.lineWidth = this.lineWidth;
            this.ctx.strokeStyle = this.waveColor;
            this.ctx.beginPath();

            const sliceWidth = this.canvas.width / this.dataArray.length;
            let x = 0;

            for (let i = 0; i < this.dataArray.length; i++) {
                const v = this.dataArray[i] / 128.0;
                const y = (v * this.canvas.height) / 2;

                if (i === 0) {
                    this.ctx.moveTo(x, y);
                } else {
                    this.ctx.lineTo(x, y);
                }

                x += sliceWidth;
            }

            this.ctx.lineTo(this.canvas.width, this.canvas.height / 2);
            this.ctx.stroke();
        };

        draw();
    }

    stopVisualization() {
        /**
         * Stop the waveform animation
         */
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }

        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    setColors(waveColor, backgroundColor) {
        /**
         * Customize waveform colors
         */
        this.waveColor = waveColor;
        this.backgroundColor = backgroundColor;
    }
}

// Export for use in dashboard
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AudioWaveform;
}
