/**
 * Export & Rendering Screen
 * Handles video rendering with resolution/format options, progress tracking, and sharing
 */

import React, { useState } from 'react';
import {
  VStack,
  HStack,
  Text,
  Button,
  Box,
  ScrollView,
  Progress,
  Radio,
  Checkbox,
  Modal,
  Icon,
  Badge,
  Divider,
} from 'native-base';
import { Ionicons } from '@expo/vector-icons';

interface ExportScreenProps {
  route: any;
  navigation: any;
}

interface ExportProgress {
  stage: 'idle' | 'encoding' | 'rendering' | 'finalizing' | 'complete';
  progress: number;
  currentFrame: number;
  totalFrames: number;
  message: string;
}

const RESOLUTIONS = [
  {
    id: '720p',
    label: 'HD 720p',
    desc: '1280 x 720 • 4 Mbps',
    value: 4000,
  },
  {
    id: '1080p',
    label: 'Full HD 1080p',
    desc: '1920 x 1080 • 8 Mbps',
    value: 8000,
  },
  {
    id: '4K',
    label: '4K Ultra HD',
    desc: '3840 x 2160 • 16 Mbps',
    value: 16000,
  },
];

const FORMATS = [
  { id: 'mp4', label: 'MP4', desc: 'Wide compatibility' },
  { id: 'mov', label: 'MOV', desc: 'Apple optimized' },
  { id: 'webm', label: 'WebM', desc: 'Web optimized' },
];

export const ExportScreen: React.FC<ExportScreenProps> = ({
  route,
  navigation,
}) => {
  const [selectedResolution, setSelectedResolution] = useState('1080p');
  const [selectedFormat, setSelectedFormat] = useState('mp4');
  const [quality, setQuality] = useState('high');
  const [includeAudio, setIncludeAudio] = useState(true);
  const [includeEffects, setIncludeEffects] = useState(true);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [progress, setProgress] = useState<ExportProgress>({
    stage: 'idle',
    progress: 0,
    currentFrame: 0,
    totalFrames: 0,
    message: 'Ready to export',
  });

  const resolutionSpec = RESOLUTIONS.find((r) => r.id === selectedResolution);
  const estimatedFileSize = Math.round(
    (resolutionSpec?.value || 8000) * (route.params?.timeline?.duration || 30) / 8 / 1024
  );
  const estimatedTime = Math.round(
    (route.params?.timeline?.duration || 30) * 1.5 * (quality === 'high' ? 1.5 : quality === 'medium' ? 1 : 0.7)
  );

  const handleStartExport = async () => {
    setExporting(true);
    setProgress({
      stage: 'encoding',
      progress: 0,
      currentFrame: 0,
      totalFrames: 0,
      message: 'Starting video encoding...',
    });

    try {
      // Simulate export stages
      for (let i = 0; i <= 100; i += 10) {
        await new Promise((resolve) => setTimeout(resolve, 500));
        setProgress({
          stage: 'encoding',
          progress: i,
          currentFrame: Math.floor((i / 100) * 1000),
          totalFrames: 1000,
          message: `Encoding: ${i}% complete`,
        });
      }

      for (let i = 0; i <= 100; i += 20) {
        await new Promise((resolve) => setTimeout(resolve, 300));
        setProgress({
          stage: 'rendering',
          progress: 50 + i / 2,
          currentFrame: 1000 + Math.floor((i / 100) * 500),
          totalFrames: 1500,
          message: `Rendering effects: ${i}% complete`,
        });
      }

      for (let i = 0; i <= 100; i += 25) {
        await new Promise((resolve) => setTimeout(resolve, 200));
        setProgress({
          stage: 'finalizing',
          progress: 75 + i / 4,
          currentFrame: 1500,
          totalFrames: 1500,
          message: `Finalizing: ${i}% complete`,
        });
      }

      setProgress({
        stage: 'complete',
        progress: 100,
        currentFrame: 1500,
        totalFrames: 1500,
        message: 'Export complete! Ready to share.',
      });
    } catch (error) {
      setProgress({
        stage: 'idle',
        progress: 0,
        currentFrame: 0,
        totalFrames: 0,
        message: 'Export failed. Please try again.',
      });
      setExporting(false);
    }
  };

  const handleShare = () => {
    // Integration with react-native-share
    // Share video to social media platforms
  };

  const handleDownload = () => {
    // Integration with react-native-fs for local storage
    // Save to device camera roll or file system
  };

  const getStageColor = (stage: string) => {
    const colors = {
      idle: 'gray',
      encoding: 'blue',
      rendering: 'purple',
      finalizing: 'green',
      complete: 'success',
    };
    return colors[stage] || 'gray';
  };

  const getStageIcon = (stage: string) => {
    const icons = {
      idle: 'radio-button-off',
      encoding: 'hourglass',
      rendering: 'refresh-circle',
      finalizing: 'checkmark-circle',
      complete: 'checkmark-done-circle',
    };
    return icons[stage] || 'radio-button-off';
  };

  return (
    <VStack flex={1} bg="white">
      {/* Header */}
      <Box bg="blue.600" p={4} safeAreaTop>
        <VStack space={1}>
          <Text fontSize="2xl" fontWeight="bold" color="white">
            Export & Render
          </Text>
          <Text color="blue.100">
            {route.params?.timeline?.duration?.toFixed(1) || '30'}s video
          </Text>
        </VStack>
      </Box>

      {exporting ? (
        /* Export Progress Screen */
        <VStack flex={1} p={6} justifyContent="center" alignItems="center" space={6}>
          <VStack space={4} w="full">
            <VStack alignItems="center" space={2}>
              <Icon
                as={Ionicons}
                name={getStageIcon(progress.stage)}
                size="16"
                color={`${getStageColor(progress.stage)}.600`}
              />
              <Text fontSize="2xl" fontWeight="bold">
                {progress.stage.charAt(0).toUpperCase() + progress.stage.slice(1)}
              </Text>
              <Text fontSize="lg" color="gray.600">
                {progress.message}
              </Text>
            </VStack>

            <VStack space={2}>
              <Box>
                <HStack justifyContent="space-between" mb={2}>
                  <Text fontWeight="bold">Progress</Text>
                  <Text fontWeight="bold" color="blue.600">
                    {progress.progress.toFixed(0)}%
                  </Text>
                </HStack>
                <Progress
                  value={progress.progress}
                  colorScheme={getStageColor(progress.stage)}
                  size="lg"
                  borderRadius="full"
                />
              </Box>

              <Box p={4} bg="gray.100" borderRadius="lg">
                <VStack space={2}>
                  <HStack justifyContent="space-between">
                    <Text fontSize="sm" color="gray.600">
                      Frames Encoded
                    </Text>
                    <Text fontWeight="bold">
                      {progress.currentFrame} / {progress.totalFrames}
                    </Text>
                  </HStack>

                  <HStack justifyContent="space-between">
                    <Text fontSize="sm" color="gray.600">
                      Estimated Time Remaining
                    </Text>
                    <Text fontWeight="bold">
                      {Math.max(
                        0,
                        Math.round(
                          estimatedTime * (1 - progress.progress / 100)
                        )
                      )}s
                    </Text>
                  </HStack>

                  <HStack justifyContent="space-between">
                    <Text fontSize="sm" color="gray.600">
                      Resolution
                    </Text>
                    <Text fontWeight="bold">{selectedResolution}</Text>
                  </HStack>
                </VStack>
              </Box>
            </VStack>

            {progress.stage === 'complete' && (
              <VStack space={2}>
                <Button
                  bg="green.600"
                  size="lg"
                  leftIcon={<Icon as={Ionicons} name="share-social" size="6" />}
                  onPress={handleShare}
                >
                  Share Video
                </Button>
                <Button
                  variant="outline"
                  borderColor="blue.600"
                  _text={{ color: 'blue.600' }}
                  leftIcon={
                    <Icon as={Ionicons} name="download" size="6" />
                  }
                  onPress={handleDownload}
                >
                  Download to Device
                </Button>
              </VStack>
            )}
          </VStack>
        </VStack>
      ) : (
        /* Export Settings Screen */
        <ScrollView flex={1} p={4}>
          <VStack space={6}>
            {/* Resolution Selection */}
            <Box>
              <Text fontWeight="bold" fontSize="lg" mb={3}>
                Video Resolution
              </Text>
              <Radio.Group
                name="resolution"
                value={selectedResolution}
                onChange={setSelectedResolution}
              >
                <VStack space={2}>
                  {RESOLUTIONS.map((res) => (
                    <Box
                      key={res.id}
                      p={3}
                      borderRadius="lg"
                      borderWidth={1}
                      borderColor={
                        selectedResolution === res.id ? 'blue.500' : 'gray.200'
                      }
                      bg={selectedResolution === res.id ? 'blue.50' : 'white'}
                    >
                      <Radio value={res.id} my={0}>
                        <VStack ml={3}>
                          <Text fontWeight="bold">{res.label}</Text>
                          <Text fontSize="xs" color="gray.600">
                            {res.desc}
                          </Text>
                        </VStack>
                      </Radio>
                    </Box>
                  ))}
                </VStack>
              </Radio.Group>
            </Box>

            {/* Format Selection */}
            <Box>
              <Text fontWeight="bold" fontSize="lg" mb={3}>
                File Format
              </Text>
              <Radio.Group
                name="format"
                value={selectedFormat}
                onChange={setSelectedFormat}
              >
                <HStack space={2}>
                  {FORMATS.map((fmt) => (
                    <Box
                      key={fmt.id}
                      flex={1}
                      p={3}
                      borderRadius="lg"
                      borderWidth={1}
                      borderColor={
                        selectedFormat === fmt.id ? 'blue.500' : 'gray.200'
                      }
                      bg={selectedFormat === fmt.id ? 'blue.50' : 'white'}
                    >
                      <Radio value={fmt.id} my={0}>
                        <VStack ml={2}>
                          <Text fontWeight="bold">{fmt.label}</Text>
                          <Text fontSize="xs" color="gray.600">
                            {fmt.desc}
                          </Text>
                        </VStack>
                      </Radio>
                    </Box>
                  ))}
                </HStack>
              </Radio.Group>
            </Box>

            {/* Quality Selection */}
            <Box>
              <Text fontWeight="bold" fontSize="lg" mb={3}>
                Encoding Quality
              </Text>
              <Radio.Group name="quality" value={quality} onChange={setQuality}>
                <VStack space={2}>
                  <Box
                    p={3}
                    borderRadius="lg"
                    borderWidth={1}
                    borderColor={quality === 'high' ? 'blue.500' : 'gray.200'}
                    bg={quality === 'high' ? 'blue.50' : 'white'}
                  >
                    <Radio value="high" my={0}>
                      <VStack ml={3}>
                        <Text fontWeight="bold">High (Slow)</Text>
                        <Text fontSize="xs" color="gray.600">
                          ~{estimatedTime * 1.5}s • Best quality
                        </Text>
                      </VStack>
                    </Radio>
                  </Box>

                  <Box
                    p={3}
                    borderRadius="lg"
                    borderWidth={1}
                    borderColor={quality === 'medium' ? 'blue.500' : 'gray.200'}
                    bg={quality === 'medium' ? 'blue.50' : 'white'}
                  >
                    <Radio value="medium" my={0}>
                      <VStack ml={3}>
                        <Text fontWeight="bold">Medium (Balanced)</Text>
                        <Text fontSize="xs" color="gray.600">
                          ~{estimatedTime}s • Balanced
                        </Text>
                      </VStack>
                    </Radio>
                  </Box>

                  <Box
                    p={3}
                    borderRadius="lg"
                    borderWidth={1}
                    borderColor={quality === 'low' ? 'blue.500' : 'gray.200'}
                    bg={quality === 'low' ? 'blue.50' : 'white'}
                  >
                    <Radio value="low" my={0}>
                      <VStack ml={3}>
                        <Text fontWeight="bold">Low (Fast)</Text>
                        <Text fontSize="xs" color="gray.600">
                          ~{Math.round(estimatedTime * 0.7)}s • Faster export
                        </Text>
                      </VStack>
                    </Radio>
                  </Box>
                </VStack>
              </Radio.Group>
            </Box>

            <Divider />

            {/* Options */}
            <Box>
              <Text fontWeight="bold" fontSize="lg" mb={3}>
                Options
              </Text>
              <VStack space={2}>
                <Checkbox
                  value="audio"
                  isChecked={includeAudio}
                  onChange={setIncludeAudio}
                >
                  <Text ml={2}>Include Audio</Text>
                </Checkbox>

                <Checkbox
                  value="effects"
                  isChecked={includeEffects}
                  onChange={setIncludeEffects}
                >
                  <Text ml={2}>Include Beat-Sync Effects</Text>
                </Checkbox>
              </VStack>
            </Box>

            {/* Export Statistics */}
            <Box p={4} bg="blue.50" borderRadius="lg">
              <VStack space={2}>
                <HStack justifyContent="space-between">
                  <Text color="gray.600">Estimated File Size</Text>
                  <Badge colorScheme="blue">{estimatedFileSize} MB</Badge>
                </HStack>

                <HStack justifyContent="space-between">
                  <Text color="gray.600">Estimated Render Time</Text>
                  <Badge colorScheme="blue">{estimatedTime}s</Badge>
                </HStack>

                <HStack justifyContent="space-between">
                  <Text color="gray.600">Video Bitrate</Text>
                  <Badge colorScheme="blue">
                    {resolutionSpec?.value} kbps
                  </Badge>
                </HStack>
              </VStack>
            </Box>

            {/* Advanced Options */}
            <Button
              variant="ghost"
              _text={{ color: 'blue.600' }}
              onPress={() => setShowAdvanced(!showAdvanced)}
            >
              {showAdvanced ? '▼' : '▶'} Advanced Options
            </Button>

            {showAdvanced && (
              <Box p={3} bg="gray.100" borderRadius="lg">
                <Text fontSize="sm" color="gray.600">
                  Frame interpolation, custom codecs, and watermark options
                  coming soon...
                </Text>
              </Box>
            )}
          </VStack>
        </ScrollView>
      )}

      {/* Action Buttons */}
      {!exporting && (
        <VStack space={3} p={4} borderTopWidth={1} borderTopColor="gray.200">
          <Button
            bg="green.600"
            size="lg"
            isLoading={exporting}
            onPress={handleStartExport}
            _text={{ fontSize: 'md', fontWeight: 'bold' }}
          >
            {exporting ? 'Exporting...' : 'Start Export'}
          </Button>

          <Button
            variant="outline"
            borderColor="blue.600"
            _text={{ color: 'blue.600' }}
            onPress={() => navigation.goBack()}
          >
            Back
          </Button>
        </VStack>
      )}
    </VStack>
  );
};

export default ExportScreen;
