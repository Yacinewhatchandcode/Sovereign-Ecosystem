
// VIOLATION: Component with no backend binding

export function PodcastPlayer() {
    const [status, setStatus] = useState('idle');
    
    // VIOLATION: Button with no API endpoint
    const handlePlay = () => {
        // TODO: Connect to real backend
        setStatus('playing');
        console.log('DUMMY: No real backend call');
    };
    
    return (
        <div>
            <button onClick={handlePlay}>Play Podcast</button>
            <button onClick={() => console.log('MOCK')}>Record</button>
        </div>
    );
}
