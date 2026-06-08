/**
 * Video upload and analysis screen
 */

import React, { useState } from 'react';
import {
  VStack,
  HStack,
  Button,
  Text,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  IconButton,
  CloseIcon,
  Box,
  FlatList,
  Pressable,
  Badge,
  ScrollView,
} from 'native-base';
import { Ionicons } from '@expo/vector-icons';
import apiClient from '../services/api';
import { useProjectStore, VideoClipMetadata } from '../services/projectStore';

interface VideoAnalysisResult {
  movement: string;
  shot_scale: string;
  colors: string[];
  energy: number;
  duration: number;
  fps: number;
}

export const VideoUploadScreen = ({ navigation }: any) => {
  const [loading, setLoading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [analyzedClips, setAnalyzedClips] = useState<
    (VideoAnalysisResult & { id: string; fileName: string })[]
  >([]);
  const [error, setError] = useState<string | null>(null);

  const { currentProject, addVideoClip } = useProjectStore();

  const handleFileSelect = (file: File) => {
    if (!selectedFiles.some((f) => f.name === file.name)) {
      setSelectedFiles([...selectedFiles, file]);
      setError(null);
    }
  };

  const handleFileRemove = (fileName: string) => {
    setSelectedFiles(selectedFiles.filter((f) => f.name !== fileName));
  };

  const analyzeSelectedClips = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select at least one video file');
      return;
    }

    setLoading(true);
    const analyzed = [];

    try {
      for (const file of selectedFiles) {
        const response = await apiClient.analyzeVideo(file);
        const clipId = `clip_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

        analyzed.push({
          id: clipId,
          fileName: file.name,
          ...response,
        });

        // Add to store
        const clipMetadata: VideoClipMetadata = {
          id: clipId,
          movement: response.movement,
          shot_scale: response.shot_scale,
          colors: response.colors,
          energy: response.energy,
          duration: response.duration,
        };
        addVideoClip(clipMetadata);
      }

      setAnalyzedClips(analyzed);
      setSelectedFiles([]);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Video analysis failed'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleProceedToMatching = async () => {
    if (analyzedClips.length === 0) {
      setError('Please analyze at least one video clip');
      return;
    }

    // Proceed to matching screen
    navigation.navigate('Matching', {
      clips: analyzedClips,
    });
  };

  const getMovementColor = (movement: string) => {
    const colors: Record<string, string> = {
      static: 'gray',
      gimbal: 'blue',
      handheld: 'orange',
      fast: 'red',
    };
    return colors[movement] || 'gray';
  };

  return (
    <VStack flex={1} bg="white">
      {/* Header */}
      <Box bg="blue.600" p={4} safeAreaTop>
        <Text fontSize="2xl" fontWeight="bold" color="white">
          Upload Video Clips
        </Text>
        <Text color="blue.100">Add and analyze your video footage</Text>
      </Box>

      <ScrollView flex={1} p={4}>
        <VStack space={4}>
          {/* File Selection Area */}
          <Box
            borderWidth={2}
            borderColor="blue.200"
            borderStyle="dashed"
            borderRadius="lg"
            p={6}
            bg="blue.50"
            alignItems="center"
            justifyContent="center"
          >
            <VStack space={3} alignItems="center" w="full">
              <Ionicons name="film" size={48} color="#3182CE" />
              <Text fontWeight="bold" fontSize="lg">
                Select Video Files
              </Text>
              <Text color="gray.600" fontSize="sm" textAlign="center">
                Tap to select multiple clips
              </Text>
              <Button
                size="md"
                bg="blue.600"
                onPress={() => {
                  // File picker would be implemented with expo-document-picker
                }}
              >
                Choose Videos
              </Button>
            </VStack>
          </Box>

          {/* Selected Files List */}
          {selectedFiles.length > 0 && (
            <Box>
              <Text fontWeight="bold" fontSize="md" mb={2}>
                Selected Files ({selectedFiles.length})
              </Text>
              <VStack space={2}>
                {selectedFiles.map((file) => (
                  <HStack
                    key={file.name}
                    bg="gray.100"
                    p={3}
                    borderRadius="lg"
                    justifyContent="space-between"
                    alignItems="center"
                  >
                    <HStack alignItems="center" space={2} flex={1}>
                      <Ionicons name="film-outline" size={20} color="#4A5568" />
                      <Text flex={1} fontSize="sm" numberOfLines={1}>
                        {file.name}
                      </Text>
                    </HStack>
                    <IconButton
                      icon={<CloseIcon />}
                      size="sm"
                      onPress={() => handleFileRemove(file.name)}
                    />
                  </HStack>
                ))}
              </VStack>
            </Box>
          )}

          {/* Error Alert */}
          {error && (
            <Alert status="error" borderRadius="lg">
              <AlertIcon />
              <VStack w="full" space={1}>
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </VStack>
              <IconButton
                icon={<CloseIcon size="md" />}
                onPress={() => setError(null)}
              />
            </Alert>
          )}

          {/* Analyzed Clips */}
          {analyzedClips.length > 0 && (
            <Box>
              <Text fontWeight="bold" fontSize="md" mb={2}>
                Analyzed Clips ({analyzedClips.length})
              </Text>
              <VStack space={3}>
                {analyzedClips.map((clip) => (
                  <Box
                    key={clip.id}
                    bg="green.50"
                    p={3}
                    borderRadius="lg"
                    borderLeftWidth={4}
                    borderLeftColor="green.400"
                  >
                    <VStack space={2}>
                      <Text fontWeight="bold" fontSize="sm">
                        {clip.fileName}
                      </Text>

                      <HStack justifyContent="space-between" flexWrap="wrap">
                        <VStack space={1}>
                          <HStack space={1} alignItems="center">
                            <Text fontSize="xs" color="gray.600">
                              Movement:
                            </Text>
                            <Badge colorScheme={getMovementColor(clip.movement)}>
                              {clip.movement}
                            </Badge>
                          </HStack>

                          <HStack space={1} alignItems="center">
                            <Text fontSize="xs" color="gray.600">
                              Shot:
                            </Text>
                            <Badge colorScheme="purple">
                              {clip.shot_scale}
                            </Badge>
                          </HStack>
                        </VStack>

                        <VStack space={1} alignItems="flex-end">
                          <Text fontSize="xs" color="gray.600">
                            Energy: {(clip.energy * 100).toFixed(0)}%
                          </Text>
                          <Text fontSize="xs" color="gray.600">
                            Duration: {clip.duration.toFixed(1)}s
                          </Text>
                        </VStack>
                      </HStack>

                      <HStack space={1} flexWrap="wrap">
                        {clip.colors.map((color) => (
                          <Badge key={color} colorScheme="gray">
                            {color}
                          </Badge>
                        ))}
                      </HStack>
                    </VStack>
                  </Box>
                ))}
              </VStack>
            </Box>
          )}
        </VStack>
      </ScrollView>

      {/* Bottom Buttons */}
      <VStack space={3} p={4} borderTopWidth={1} borderTopColor="gray.200">
        {selectedFiles.length > 0 && (
          <Button
            bg="blue.600"
            isLoading={loading}
            isDisabled={loading}
            onPress={analyzeSelectedClips}
            _text={{ fontSize: 'md' }}
            p={3}
          >
            {loading ? (
              <>
                <Spinner color="white" mr={2} />
                Analyzing...
              </>
            ) : (
              `Analyze ${selectedFiles.length} Clip${selectedFiles.length !== 1 ? 's' : ''}`
            )}
          </Button>
        )}

        {analyzedClips.length > 0 && (
          <Button
            bg="green.600"
            onPress={handleProceedToMatching}
            _text={{ fontSize: 'md' }}
            p={3}
          >
            Proceed to Auto-Matching
          </Button>
        )}

        <Button
          variant="outline"
          onPress={() => navigation.goBack()}
          _text={{ color: 'blue.600' }}
        >
          Back
        </Button>
      </VStack>
    </VStack>
  );
};
