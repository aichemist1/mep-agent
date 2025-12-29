import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, Image, TextInput, TouchableOpacity, ScrollView, Alert, ActivityIndicator, KeyboardAvoidingView, Platform } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { uploadFiles, refineText, sendReport } from '../services/api';

export default function PreviewScreen() {
    const route = useRoute();
    const navigation = useNavigation();
    const { photoUri, audioUri } = route.params;

    const [email, setEmail] = useState('');
    const [subject, setSubject] = useState('MEP Field Report');
    const [transcript, setTranscript] = useState('');
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState('');
    const [imagePath, setImagePath] = useState(null);
    const [audioPath, setAudioPath] = useState(null);
    const [step, setStep] = useState('upload'); // upload, review

    // Auto-upload on mount
    useEffect(() => {
        uploadAndTranscribe();
    }, []);

    const uploadAndTranscribe = async () => {
        setLoading(true);
        setStatus('Uploading and transcribing...');
        try {
            const data = await uploadFiles(photoUri, audioUri);
            setTranscript(data.transcript);
            setImagePath(data.image_path);
            setAudioPath(data.audio_path);
            setStatus('');
            setStep('review');
        } catch (error) {
            console.error(error);
            Alert.alert("Error", error.error || "Failed to upload");
            navigation.goBack();
        } finally {
            setLoading(false);
        }
    };

    const handleRefine = async () => {
        setLoading(true);
        setStatus("Refining with AI...");
        try {
            const data = await refineText(transcript);
            setTranscript(data.refined_text);
            setStatus('');
        } catch (error) {
            Alert.alert("Refine Error", error.error || "Failed to refine");
        } finally {
            setLoading(false);
        }
    };

    const handleSend = async () => {
        if (!email) {
            Alert.alert("Error", "Please enter recipient email");
            return;
        }

        setLoading(true);
        setStatus("Sending email...");
        try {
            await sendReport(email, subject, transcript, imagePath, audioPath);
            Alert.alert("Success", "Report sent successfully!", [
                { text: "OK", onPress: () => navigation.popToTop() }
            ]);
        } catch (error) {
            console.error(error);
            Alert.alert("Send Error", error.error || "Failed to send");
        } finally {
            setLoading(false);
        }
    };

    return (
        <KeyboardAvoidingView
            behavior={Platform.OS === "ios" ? "padding" : "height"}
            style={{ flex: 1 }}
        >
            <ScrollView contentContainerStyle={styles.container}>
                <Image source={{ uri: photoUri }} style={styles.thumbnail} />

                {loading && (
                    <View style={styles.loadingContainer}>
                        <ActivityIndicator size="large" color="#2563eb" />
                        <Text style={styles.loadingText}>{status}</Text>
                    </View>
                )}

                {!loading && step === 'review' && (
                    <View style={styles.form}>
                        <Text style={styles.label}>Transcription</Text>
                        <TextInput
                            style={[styles.input, styles.textArea]}
                            multiline
                            value={transcript}
                            onChangeText={setTranscript}
                        />

                        <TouchableOpacity style={styles.refineBtn} onPress={handleRefine}>
                            <Text style={styles.refineText}>✨ Refine with AI</Text>
                        </TouchableOpacity>

                        <Text style={styles.label}>Recipient Email</Text>
                        <TextInput
                            style={styles.input}
                            placeholder="supervisor@example.com"
                            value={email}
                            onChangeText={setEmail}
                            autoCapitalize="none"
                            keyboardType="email-address"
                        />

                        <Text style={styles.label}>Subject</Text>
                        <TextInput
                            style={styles.input}
                            value={subject}
                            onChangeText={setSubject}
                        />

                        <TouchableOpacity style={styles.sendBtn} onPress={handleSend}>
                            <Text style={styles.sendText}>Send Report</Text>
                        </TouchableOpacity>
                    </View>
                )}
            </ScrollView>
        </KeyboardAvoidingView>
    );
}

const styles = StyleSheet.create({
    container: {
        flexGrow: 1,
        padding: 20,
        backgroundColor: '#f3f4f6'
    },
    thumbnail: {
        width: 100,
        height: 100,
        borderRadius: 10,
        alignSelf: 'center',
        marginBottom: 20
    },
    loadingContainer: {
        alignItems: 'center',
        marginTop: 50
    },
    loadingText: {
        marginTop: 10,
        color: '#6b7280'
    },
    form: {
        width: '100%'
    },
    label: {
        fontWeight: 'bold',
        marginBottom: 5,
        marginTop: 15,
        color: '#374151'
    },
    input: {
        backgroundColor: '#fff',
        borderWidth: 1,
        borderColor: '#e5e7eb',
        borderRadius: 8,
        padding: 10,
        fontSize: 16
    },
    textArea: {
        minHeight: 150,
        textAlignVertical: 'top'
    },
    refineBtn: {
        alignSelf: 'flex-end',
        padding: 8
    },
    refineText: {
        color: '#2563eb',
        fontWeight: '600'
    },
    sendBtn: {
        backgroundColor: '#2563eb',
        padding: 15,
        borderRadius: 8,
        alignItems: 'center',
        marginTop: 30,
        marginBottom: 50
    },
    sendText: {
        color: '#fff',
        fontWeight: 'bold',
        fontSize: 18
    }
});
