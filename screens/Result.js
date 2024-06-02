import React from 'react';
import { View, Text, Image, StyleSheet } from 'react-native';
import cropped_image from '/Users/efekalayci/BBM479Pressure_Ulcers/_cropped.jpg'
import original_image from '/Users/efekalayci/BBM479Pressure_Ulcers/original_image.png'
import { useRoute } from '@react-navigation/native';


const Result = ({route}) => {
    const { n0, n1, n2, n3 } = route.params;

  // Dummy float değerleri
  //   const floatValues = [l0,l1,l2,l3];

  const floatValues = [n0, n1, n2, n3];

  return (
    <View style={styles.container}>
      <Image
        source={original_image}
        style={styles.image}
      />
      <View style={styles.textContainer}>
        <Text style={styles.text}>1st Degree With {floatValues[0]} Prob.</Text>
        <Text style={styles.text}>2nd Degree With {floatValues[1]} Prob.</Text>
        <Text style={styles.text}>3rd Degree With {floatValues[2]} Prob.</Text>
        <Text style={styles.text}>4th Degree With {floatValues[3]} Prob.</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  image: {
    width: 256,
    height: 256,
    resizeMode: 'cover',
  },
  floatValue: {
    fontSize: 18,   
    marginTop: 10,
  },
  textContainer: {
    alignItems: 'center',
  },
  text: {
    fontSize: 18,
    color: '#333',
    marginBottom: 10,
    fontWeight: 'bold',
  },
});

export default Result;