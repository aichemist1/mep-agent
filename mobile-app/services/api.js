import axios from 'axios';
import { Platform } from 'react-native';

// REPLACE WITH YOUR COMPUTER'S LOCAL IP ADDRESS IF TESTING ON PHYSICAL DEVICE
const BASE_URL = 'http://192.168.1.239:5000';

const api = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'multipart/form-data',
    },
});

export const uploadFiles = async (imageUri, audioUri) => {
    const formData = new FormData();

    // Image
    const filename = imageUri.split('/').pop();
    const match = /\.(\w+)$/.exec(filename);
    const type = match ? `image/${match[1]}` : `image`;

    formData.append('image', {
        uri: Platform.OS === 'ios' ? imageUri.replace('file://', '') : imageUri,
        name: filename,
        type,
    });

    // Audio
    if (audioUri) {
        const audioName = audioUri.split('/').pop();
        const audioType = 'audio/m4a'; // Expo AV records m4a on iOS usually
        formData.append('audio', {
            uri: audioUri,
            name: audioName,
            type: audioType,
        });
    }

    try {
        const response = await api.post('/api/upload', formData);
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : error;
    }
};

export const refineText = async (text) => {
    try {
        const response = await api.post('/api/refine', { text }, {
            headers: { 'Content-Type': 'application/json' }
        });
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : error;
    }
}

export const sendReport = async (email, subject, text, imagePath, audioPath) => {
    try {
        const response = await api.post('/api/send', {
            email,
            subject,
            text,
            image_path: imagePath,
            audio_path: audioPath
        }, {
            headers: { 'Content-Type': 'application/json' }
        });
        return response.data;
    } catch (error) {
        throw error.response ? error.response.data : error;
    }
};

export default api;
