import React from 'react';
import { View, Text, StyleSheet,Image } from 'react-native';
import { useRoute } from '@react-navigation/native';
import logoImg from "../uploads/image.jpg"

const Segmentation = ({ navigation }) => {
    const route = useRoute();
    const { image } = route.params;
    return (
        <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
      <Image source={image ? { uri: image } : logoImg} style={{ width: 200, height: 300 }} />

        </View>
      );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  centeredText: {
    fontSize: 18,
    textAlign: 'center',
  },
});

export default Segmentation;
