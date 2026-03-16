import React from 'react';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error("Uncaught error:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen flex items-center justify-center bg-red-900 text-white p-10">
                    <div>
                        <h1 className="text-3xl font-bold mb-4">Something went wrong.</h1>
                        <pre className="bg-black/50 p-4 rounded overflow-auto max-w-2xl">
                            {this.state.error && this.state.error.toString()}
                        </pre>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
