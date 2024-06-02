import React , { useState }from 'react';
import { View, Button, StyleSheet,Image,TouchableOpacity,ActivityIndicator, Text} from 'react-native';
//import {launchImageLibrary} from 'react-native-image-picker';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import logoImg from "../assets/hu.png"
import ImagePicker, { openPicker } from 'react-native-image-crop-picker';
import RNFetchBlob from 'rn-fetch-blob';
const ipAddress = "172.20.10.2"
const port = "5000"
const Home = ({navigation}) => {
  const [isButtonEnabled, setButtonEnabled] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [segmentedImage, setSegmentedImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [n0, setN0] = useState('');
  const [n1, setN1] = useState('');
  const [n2, setN2] = useState('');
  const [n3, setN3] = useState(''); 
  const [l0, setL0] = useState('');
  const [l1, setL1] = useState('');
  const [l2, setL2] = useState('');
  const [l3, setL3] = useState('');


  const takePhotoFromCamera = () => {
    ImagePicker.openCamera({
      width: 300,
      height: 300,
      cropping: false
  }).then(image => {
      console.log(image.path);
      setSelectedImage(image.path);
      uploadImage(image.path).then(() => {
        setButtonEnabled(false);
        getFile();
      });
  }).catch(error => {
      console.error("Error opening camera: ", error);
  });
  }
  //RNFetchBlob.fetch('GET', `http://${ipAddress}:${port}/get_file`)

const getFile = async () => {
  try {
    setLoading(true);
    setButtonEnabled(false);
    const response = await RNFetchBlob.fetch('GET', `http://${ipAddress}:${port}/get_file`);
    
    const responseData = JSON.parse(response.data);
    const { file_name, file_content, values: valuesString } = responseData;

    // Decode base64 file content
    const imageBase64 = 'data:image/png;base64,' + file_content;
    console.log("asda")
    // Split the values string into separate variables
    const [newL0, newL1, newL2, newL3, newR0, newR1, newR2, newR3] = valuesString.split(' ');
    setN0(newR0);
    setN1(newR1);
    setN2(newR2);
    setN3(newR3);
    setL0(newL0);
    setL1(newL1);
    setL2(newL2);
    setL3(newL3);

    console.log(l0,l1,l2,l3,newL0)
    console.log(l0,l1,l2,l3,n0,n1,n2,n3)
    
    // Update states
    setSegmentedImage(imageBase64);
  } catch (error) {
    console.error('Error downloading file:', error);
  } finally {
    setLoading(false);
    setButtonEnabled(true);  }
};

const uploadImage = async (imagePath) => {
  const formData = new FormData();
  formData.append('file', {
    uri: imagePath,
    name: 'image.jpg',
    type: 'image/jpeg'
  });

  try {
    const response = await fetch(`http://${ipAddress}:${port}/upload`, {
      method: 'POST',
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      body: formData,
    });
    
    const data = await response.text();
    console.log(data); // Sunucudan gelen yanıtı konsola yazdır
  } catch (error) {
    console.error('Hata:', error);
  }
};
const selectFromGallery = () => {
  ImagePicker.openPicker({
      width: 300,
      height: 300,
      cropping: false
  }).then(image => {
      console.log(image.path);
      setSelectedImage(image.path)
      uploadImage(image.path).then(() => {
        setButtonEnabled(false);
        getFile();
      });
  });
}
  const handleButton1Press = () => {
    navigation.navigate('Segmentation');}
  

  const handleButton2Press = () => {
    // Button 2'ye tıklanınca yapılacak işlemler
    console.log('Button 2 pressed');
  };


  return (
    <View style={styles.container}>
      {loading && <ActivityIndicator size="large" color="#0000ff" />}
      <TouchableOpacity style={styles.panelButton} onPress={takePhotoFromCamera}>
      <Text style={styles.panelButtonTitle}>Take Photo</Text>
      </TouchableOpacity>
      
      <TouchableOpacity style={styles.panelButton} onPress={selectFromGallery}>
      <Text style={styles.panelButtonTitle}>Select Photo From Gallery</Text>
      </TouchableOpacity>

      <Image source={selectedImage ? { uri: selectedImage } : logoImg} style={{ width: 200, height: 300 }} />
      <TouchableOpacity
        onPress={() => navigation.navigate('Segmentation',{image:segmentedImage,})}
        disabled={!isButtonEnabled}
        style={[
          styles.button,  
          { backgroundColor: isButtonEnabled ? '#FF6347' : 'lightgray' },
        ]}>
        <Text style={styles.buttonText}>Segmentation</Text>
      </TouchableOpacity>

      <TouchableOpacity
          onPress={() => navigation.navigate('Attention', {
            l0,
            l1,
            l2,
            l3,
          })}//
        disabled={!isButtonEnabled}
        style={[
          styles.button,
          { backgroundColor: isButtonEnabled ? '#FF6347' : 'lightgray' },
        ]}>
        <Text style={styles.buttonText}>Attention Result</Text>
      </TouchableOpacity>

      <TouchableOpacity
        onPress={() => navigation.navigate('Result', {
          n0,
          n1,
          n2,
          n3,
        })}//  onPress={() => navigation.navigate('Result',{l0:level0,l1:level1, l2: level2, l3: level3})}
        disabled={!isButtonEnabled}
        style={[
          styles.button,
          { backgroundColor: isButtonEnabled ? '#FF6347' : 'lightgray' },
        ]}>
        <Text style={styles.buttonText}>Results</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  panelButtonTitle: {
    fontSize: 17,
    fontWeight: 'bold',
    color: 'white',
  },
  panelButton: {
    padding: 13,
    borderRadius: 10,
    backgroundColor: '#FF6347',
    alignItems: 'center',
    marginVertical: 7,
    width: '90%',
  },
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor : 'white'
  },
  button: {
    padding: 10,
    borderRadius: 5,
    margin: 5,
    width: '90%',
  },
  buttonText: {
    color: 'white',
    textAlign: 'center',
  },
});

export default Home;
