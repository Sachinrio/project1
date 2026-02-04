import { useState } from 'react';
import { Upload, X, Image as ImageIcon, Loader2 } from 'lucide-react';

export default function ImageGalleryUploader({ images = [], onChange }) {
    const [uploading, setUploading] = useState(false);

    const handleFileSelect = async (e) => {
        const files = Array.from(e.target.files);
        if (files.length === 0) return;

        setUploading(true);
        const newUrls = [];

        try {
            // Upload files sequentially or in parallel
            for (const file of files) {
                const formData = new FormData();
                formData.append('file', file);

                const response = await fetch('/api/v1/upload', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) throw new Error('Upload failed');

                const data = await response.json();

                if (data.url) {
                    newUrls.push(data.url);
                }
            }

            // Update parent state
            onChange([...images, ...newUrls]);
        } catch (error) {
            console.error("Upload failed", error);
            // Optionally handle error state here
        } finally {
            setUploading(false);
            // Reset input
            e.target.value = '';
        }
    };

    const removeImage = (indexToRemove) => {
        onChange(images.filter((_, index) => index !== indexToRemove));
    };

    return (
        <div className="space-y-4">
            {/* Grid of Images */}
            {images.length > 0 && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {images.map((url, index) => (
                        <div key={index} className="relative group aspect-video bg-slate-900 rounded-xl overflow-hidden border border-slate-700">
                            <img src={url} alt={`Gallery ${index}`} className="w-full h-full object-cover" />
                            <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                <button
                                    onClick={() => removeImage(index)}
                                    className="p-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500 hover:text-white transition-colors"
                                >
                                    <X size={20} />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Upload Area */}
            <div className="relative">
                <input
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={handleFileSelect}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10 disabled:cursor-not-allowed"
                    disabled={uploading}
                />
                <div className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center text-center transition-all ${uploading ? 'border-primary-500/50 bg-primary-500/5' : 'border-slate-700 hover:border-primary-500/50 hover:bg-slate-800/50 bg-slate-900/30'}`}>
                    {uploading ? (
                        <>
                            <Loader2 className="animate-spin text-primary-500 mb-2" size={32} />
                            <p className="text-slate-400 text-sm font-bold">Uploading images...</p>
                        </>
                    ) : (
                        <>
                            <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center mb-3 text-slate-400">
                                <ImageIcon size={24} />
                            </div>
                            <h4 className="text-white font-bold text-sm mb-1">Click to upload photos</h4>
                            <p className="text-slate-500 text-xs">Jpg, Png, Webp (Max 5MB each)</p>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
