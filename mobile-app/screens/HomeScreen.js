import React, { useState, useEffect, useRef } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, Button, Image, ActivityIndicator, Alert } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { Audio } from 'expo-av';
import { useNavigation } from '@react-navigation/native';

export default function HomeScreen() {
    const [permission, requestPermission] = useCameraPermissions();
    const [recording, setRecording] = useState();
    const [isRecording, setIsRecording] = useState(false);
    const [photo, setPhoto] = useState(null);
    const [audioUri, setAudioUri] = useState(null);
    const cameraRef = useRef(null);
    const navigation = useNavigation();

    if (!permission) {
        // Camera permissions are still loading
        return <View />;
    }

    if (!permission.granted) {
        // Camera permissions are not granted yet
        return (
            <View style={styles.container}>
                <Text style={{ textAlign: 'center', marginBottom: 20 }}>We need your permission to show the camera</Text>
                <Button onPress={requestPermission} title="grant permission" />
            </View>
        );
    }

    const takePicture = async () => {
        if (cameraRef.current) {
            try {
                const data = await cameraRef.current.takePictureAsync();
                setPhoto(data.uri);
            } catch (e) {
                Alert.alert("Error", "Failed to take picture");
            }
        }
    };

    const startRecording = async () => {
        try {
            await Audio.requestPermissionsAsync();
            await Audio.setAudioModeAsync({
                allowsRecordingIOS: true,
                playsInSilentModeIOS: true,
            });

            const { recording } = await Audio.Recording.createAsync(
                Audio.RecordingOptionsPresets.HIGH_QUALITY
            );
            setRecording(recording);
            setIsRecording(true);
        } catch (err) {
            console.error('Failed to start recording', err);
        }
    };

    const stopRecording = async () => {
        if (!recording) return;
        setIsRecording(false);
        await recording.stopAndUnloadAsync();
        const uri = recording.getURI();
        setRecording(undefined);
        setAudioUri(uri);
        Alert.alert("Audio Recorded", "Voice note saved.");
    };

    const reset = () => {
        setPhoto(null);
        setAudioUri(null);
    };

    const goToPreview = () => {
        if (!photo || !audioUri) {
            Alert.alert("Missing Info", "Please take a photo AND record a voice note.");
            return;
        }
        navigation.navigate('Preview', { photoUri: photo, audioUri: audioUri });
        reset(); // Clear state so when we come back specific to this screen it's fresh? Or keep? 
        // Actually keep reset() inside navigate success or let Preview handle "Back".
        // For now, let's NOT reset immediately so if they go back they see it.
        // But we should reset if they successfully submitted.
        // Let's remove reset() here.
    };

    if (photo) {
        return (
            <View style={styles.previewContainer}>
                <Image source={{ uri: photo }} style={styles.previewImage} />
                <View style={styles.controls}>
                    <TouchableOpacity style={styles.button} onPress={() => setPhoto(null)}>
                        <Text style={styles.text}>Retake Photo</Text>
                    </TouchableOpacity>
                </View>

                <View style={styles.audioSection}>
                    <Text style={styles.label}>{audioUri ? "Audio Recorded ✅" : "Record Voice Note"}</Text>
                    <TouchableOpacity
                        style={[styles.recordButton, isRecording && styles.recordingBtn, audioUri && styles.recordedBtn]}
                        onPress={isRecording ? stopRecording : startRecording}
                    >
                        <Text style={styles.recordText}>
                            {isRecording ? "Stop Recording" : (audioUri ? "Re-record" : "Start Recording")}
                        </Text>
                    </TouchableOpacity>
                </View>

                <TouchableOpacity
                    style={[styles.nextButton, (!audioUri) && styles.disabledBtn]}
                    onPress={goToPreview}
                    disabled={!audioUri}
                >
                    <Text style={styles.nextText}>Next: Preview & Send</Text>
                </TouchableOpacity>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            <CameraView style={styles.camera} ref={cameraRef}>
                <View style={styles.buttonContainer}>
                    <TouchableOpacity style={styles.captureButton} onPress={takePicture}>
                    </TouchableOpacity>
                </View>
            </CameraView>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
        backgroundColor: '#000',
    },
    camera: {
        flex: 1,
    },
    buttonContainer: {
        flex: 1,
        flexDirection: 'row',
        backgroundColor: 'transparent',
        justifyContent: 'center',
        margin: 64,
    },
    captureButton: {
        alignSelf: 'flex-end',
        width: 70,
        height: 70,
        borderRadius: 35,
        backgroundColor: '#fff',
        borderWidth: 4,
        borderColor: '#c0c0c0',
    },
    text: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#000',
    },
    previewContainer: {
        flex: 1,
        backgroundColor: '#f3f4f6',
        alignItems: 'center',
        padding: 20
    },
    previewImage: {
        width: '100%',
        height: 300,
        borderRadius: 10,
        marginTop: 50,
        marginBottom: 20
    },
    controls: {
        flexDirection: 'row',
        marginBottom: 20
    },
    button: {
        backgroundColor: '#e5e7eb',
        padding: 10,
        borderRadius: 8,

    },
    audioSection: {
        width: '100%',
        alignItems: 'center',
        marginBottom: 30,
        padding: 20,
        backgroundColor: '#fff',
        borderRadius: 10
    },
    label: {
        fontSize: 16,
        marginBottom: 10
    },
    recordButton: {
        backgroundColor: '#2563eb',
        paddingHorizontal: 20,
        paddingVertical: 15,
        borderRadius: 25,
        minWidth: 150,
        alignItems: 'center'
    },
    recordingBtn: {
        backgroundColor: '#ef4444'
    },
    recordedBtn: {
        backgroundColor: '#10b981'
    },
    recordText: {
        color: '#fff',
        fontWeight: 'bold',
        fontSize: 16
    },
    nextButton: {
        backgroundColor: '#2563eb',
        width: '100%',
        padding: 15,
        borderRadius: 8,
        alignItems: 'center',
        position: 'absolute',
        bottom: 40
    },
    disabledBtn: {
        backgroundColor: '#9ca3af'
    },
    nextText: {
        color: '#fff',
        fontWeight: 'bold',
        fontSize: 18
    }
});
