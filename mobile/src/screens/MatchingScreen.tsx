/**
 * MatchingScreen.tsx
 * Displays auto-matched video clips with similarity scores and adjustment interface
 */

import React, { useState } from 'react';
import {
  VStack,
  HStack,
  Box,
  Text,
  Button,
  Progress,
  Modal,
  FormControl,
  Slider,
  ScrollView,
  Pressable,
  Badge,
  AlertDialog,
  Center,
  Spinner,
} from 'native-base';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useProjectStore } from '../services/projectStore';

interface MatchedClip {
  section: string;
  clip_id: string;
  score: number;
  alternatives?: Array<{ clip_id: string; score: number }>;
}

interface MatchingResult {
  matches: MatchedClip[];
  overall_score: number;
}

export const MatchingScreen = ({ navigation, route }: any) => {
  const { matches: initialMatches, overallScore } = route.params;
  const [matches, setMatches] = useState<MatchedClip[]>(initialMatches);
  const [overallMatchScore, setOverallMatchScore] = useState(overallScore);
  const [selectedMatch, setSelectedMatch] = useState<MatchedClip | null>(null);
  const [showAlternatives, setShowAlternatives] = useState(false);
  const [manualScoreAdjustments, setManualScoreAdjustments] = useState<Record<string, number>>({});
  const [isProcessing, setIsProcessing] = useState(false);

  const { currentProject, updateMatchResults } = useProjectStore();

  const getScoreColor = (score: number): string => {
    if (score >= 0.85) return 'green';
    if (score >= 0.7) return 'amber';
    if (score >= 0.5) return 'orange';
    return 'red';
  };

  const getQualityLabel = (score: number): string => {
    if (score >= 0.85) return 'Excellent';
    if (score >= 0.7) return 'Good';
    if (score >= 0.5) return 'Fair';
    return 'Poor';
  };

  const handleManualScoreAdjustment = (sectionId: string, newScore: number) => {
    setManualScoreAdjustments({
      ...manualScoreAdjustments,
      [sectionId]: newScore,
    });

    // Update matches with new score
    const updatedMatches = matches.map((match) =>
      match.section === sectionId ? { ...match, score: newScore } : match
    );
    setMatches(updatedMatches);

    // Recalculate overall score
    const newOverallScore = updatedMatches.reduce((acc, m) => acc + m.score, 0) / updatedMatches.length;
    setOverallMatchScore(newOverallScore);
  };

  const handleSwapClip = (section: string, alternativeClipId: string) => {
    const updatedMatches = matches.map((match) =>
      match.section === section
        ? { ...match, clip_id: alternativeClipId, score: 0.8 } // Estimate new score
        : match
    );
    setMatches(updatedMatches);
    setShowAlternatives(false);
  };

  const handleProceedToTimeline = async () => {
    setIsProcessing(true);
    try {
      // Save matching results
      await updateMatchResults({
        clipOrder: matches.map((m) => m.clip_id),
        matches: matches,
        score: overallMatchScore,
      });

      // Navigate to timeline editor
      navigation.navigate('Timeline', {
        matches: matches,
        overallScore: overallMatchScore,
      });
    } catch (error) {
      console.error('Error proceeding to timeline:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <VStack flex={1} bg="white">
      {/* Header */}
      <Box bg="gradient.blue" p={4} safeAreaTop>
        <VStack space={2}>
          <Text fontSize="2xl" fontWeight="bold" color="white">
            Auto-Match Results
          </Text>
          <HStack justifyContent="space-between" alignItems="center">
            <Text color="blue.100">Overall Match Quality</Text>
            <Badge
              colorScheme={getScoreColor(overallMatchScore)}
              rounded="full"
              p={2}
            >
              {(overallMatchScore * 100).toFixed(0)}%
            </Badge>
          </HStack>
        </VStack>
      </Box>

      <ScrollView flex={1} p={4}>
        <VStack space={4}>
          {/* Overall Score Card */}
          <Box bg="blue.50" p={4} borderRadius="lg" borderLeftWidth={4} borderLeftColor="blue.400">
            <VStack space={3}>
              <HStack justifyContent="space-between" alignItems="center">
                <Text fontWeight="bold" fontSize="lg">
                  Overall Score
                </Text>
                <Text fontSize="2xl" fontWeight="bold" color="blue.600">
                  {getQualityLabel(overallMatchScore)}
                </Text>
              </HStack>
              <Progress
                value={overallMatchScore * 100}
                colorScheme={getScoreColor(overallMatchScore)}
                size="lg"
              />
              <HStack space={3} justifyContent="space-between">
                <VStack space={1} alignItems="center">
                  <Text fontSize="xs" color="gray.600">
                    Average Score
                  </Text>
                  <Text fontWeight="bold">{(overallMatchScore * 100).toFixed(1)}%</Text>
                </VStack>
                <VStack space={1} alignItems="center">
                  <Text fontSize="xs" color="gray.600">
                    Total Sections
                  </Text>
                  <Text fontWeight="bold">{matches.length}</Text>
                </VStack>
                <VStack space={1} alignItems="center">
                  <Text fontSize="xs" color="gray.600">
                    Clips Used
                  </Text>
                  <Text fontWeight="bold">{new Set(matches.map((m) => m.clip_id)).size}</Text>
                </VStack>
              </HStack>
            </VStack>
          </Box>

          {/* Matched Clips List */}
          <VStack space={3}>
            <Text fontWeight="bold" fontSize="lg">
              Section Matches
            </Text>

            {matches.map((match, index) => (
              <Box
                key={`${match.section}-${index}`}
                bg="white"
                p={4}
                borderRadius="lg"
                borderWidth={1}
                borderColor="gray.200"
              >
                <VStack space={3}>
                  {/* Section Header */}
                  <HStack justifyContent="space-between" alignItems="center">
                    <VStack space={1} flex={1}>
                      <Text fontWeight="bold" fontSize="md">
                        {match.section.charAt(0).toUpperCase() + match.section.slice(1)}
                      </Text>
                      <Text fontSize="sm" color="gray.600">
                        Clip ID: {match.clip_id}
                      </Text>
                    </VStack>
                    <Badge
                      colorScheme={getScoreColor(match.score)}
                      p={2}
                      borderRadius="full"
                    >
                      {(match.score * 100).toFixed(0)}%
                    </Badge>
                  </HStack>

                  {/* Score Bar */}
                  <Progress value={match.score * 100} colorScheme={getScoreColor(match.score)} />

                  {/* Manual Adjustment */}
                  <FormControl>
                    <FormControl.Label _text={{ fontSize: 'xs' }}>
                      Fine-tune Score
                    </FormControl.Label>
                    <Slider
                      defaultValue={match.score * 100}
                      minValue={0}
                      maxValue={100}
                      step={5}
                      onChange={(value) =>
                        handleManualScoreAdjustment(match.section, value / 100)
                      }
                      accessibilityLabel="Match score slider"
                    >
                      <Slider.Track>
                        <Slider.FilledTrack />
                      </Slider.Track>
                      <Slider.Thumb />
                    </Slider>
                  </FormControl>

                  {/* Action Buttons */}
                  <HStack space={2}>
                    <Button
                      size="sm"
                      variant="outline"
                      flex={1}
                      startIcon={
                        <MaterialCommunityIcons name="swap-horizontal" size={16} />
                      }
                      onPress={() => {
                        setSelectedMatch(match);
                        setShowAlternatives(true);
                      }}
                    >
                      Swap Clip
                    </Button>
                    <Button
                      size="sm"
                      flex={1}
                      startIcon={<MaterialCommunityIcons name="eye" size={16} />}
                      onPress={() => {
                        // Navigate to clip preview
                        navigation.navigate('ClipPreview', { clipId: match.clip_id });
                      }}
                    >
                      Preview
                    </Button>
                  </HStack>
                </VStack>
              </Box>
            ))}
          </VStack>

          {/* Statistics */}
          <Box bg="gray.50" p={4} borderRadius="lg">
            <VStack space={2}>
              <Text fontWeight="bold">Statistics</Text>
              <HStack justifyContent="space-between">
                <Text fontSize="sm" color="gray.600">
                  Highest Match:
                </Text>
                <Text fontWeight="bold">
                  {(Math.max(...matches.map((m) => m.score)) * 100).toFixed(1)}%
                </Text>
              </HStack>
              <HStack justifyContent="space-between">
                <Text fontSize="sm" color="gray.600">
                  Lowest Match:
                </Text>
                <Text fontWeight="bold">
                  {(Math.min(...matches.map((m) => m.score)) * 100).toFixed(1)}%
                </Text>
              </HStack>
            </VStack>
          </Box>
        </VStack>
      </ScrollView>

      {/* Bottom Buttons */}
      <VStack space={3} p={4} borderTopWidth={1} borderTopColor="gray.200">
        <Button
          bg="green.600"
          isLoading={isProcessing}
          onPress={handleProceedToTimeline}
          _text={{ fontSize: 'md' }}
          p={3}
        >
          {isProcessing ? 'Processing...' : 'Proceed to Timeline Editor'}
        </Button>

        <Button variant="outline" onPress={() => navigation.goBack()}>
          Back to Video Upload
        </Button>
      </VStack>

      {/* Alternatives Modal */}
      <Modal isOpen={showAlternatives} onClose={() => setShowAlternatives(false)}>
        <Modal.Content maxWidth="90%">
          <Modal.Header>Select Alternative Clip</Modal.Header>
          <Modal.Body>
            {selectedMatch?.alternatives && selectedMatch.alternatives.length > 0 ? (
              <VStack space={2}>
                {selectedMatch.alternatives.map((alt) => (
                  <Pressable
                    key={alt.clip_id}
                    p={3}
                    bg="blue.50"
                    borderRadius="lg"
                    onPress={() => handleSwapClip(selectedMatch.section, alt.clip_id)}
                  >
                    <HStack justifyContent="space-between">
                      <Text>{alt.clip_id}</Text>
                      <Badge colorScheme={getScoreColor(alt.score)}>
                        {(alt.score * 100).toFixed(0)}%
                      </Badge>
                    </HStack>
                  </Pressable>
                ))}
              </VStack>
            ) : (
              <Center>
                <Text color="gray.600">No alternatives available</Text>
              </Center>
            )}
          </Modal.Body>
          <Modal.Footer>
            <Button
              variant="ghost"
              colorScheme="blueGray"
              onPress={() => setShowAlternatives(false)}
            >
              Close
            </Button>
          </Modal.Footer>
        </Modal.Content>
      </Modal>
    </VStack>
  );
};
