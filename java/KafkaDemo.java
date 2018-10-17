import java.util.Arrays;
import java.util.Locale;
import java.util.Properties;
import java.util.concurrent.CountDownLatch;

import org.apache.kafka.common.serialization.Serde;
import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.KeyValue;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.kstream.KStream;
import org.apache.kafka.streams.kstream.KTable;
import org.apache.kafka.streams.kstream.KeyValueMapper;
import org.apache.kafka.streams.kstream.Produced;
import org.apache.kafka.streams.kstream.ValueMapper;
import org.apache.kafka.streams.kstream.ValueMapperWithKey;

import kafka.tools.ConsoleConsumer.ConsumerConfig;

public class KafkaDemo {

	public static void main(String[] args) {
		System.out.println("Begin...");
		Properties properties = new Properties();
		properties.put(StreamsConfig.APPLICATION_ID_CONFIG, "streams-wordcount");
		properties.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
		properties.put(StreamsConfig.CACHE_MAX_BYTES_BUFFERING_CONFIG, 0);
		properties.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass().getName());
		properties.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG,Serdes.String().getClass().getName());
		properties.put(org.apache.kafka.clients.consumer.ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
		
		StreamsBuilder builder = new StreamsBuilder();
		KStream<String, String> source = builder.stream("streams-input");
		
		KTable<String, Long> counts = source.flatMapValues(new ValueMapper<String, Iterable<String>>() {
			@Override
			public Iterable<String> apply(String value) {
				return Arrays.asList(value.toLowerCase(Locale.getDefault()).split(" "));
			}
		}).map(new KeyValueMapper<String, String, KeyValue<String, String>>() {
			@Override
			public KeyValue<String, String> apply(String key, String value) {
				return new KeyValue<String, String>(value, value);
			}
		}).groupByKey().count();
		
		counts.toStream().to("streams-output", Produced.with(Serdes.String(), Serdes.Long()));
		
		KafkaStreams streams = new KafkaStreams(builder.build(), properties);
		CountDownLatch latch = new CountDownLatch(1);
		
		Runtime.getRuntime().addShutdownHook(new Thread("streams-wordcount-shutdown-hook") {
			@Override
			public void run() {
				streams.close();
				latch.countDown();
			}
		});
		
		try {
			streams.start();
			latch.await();
		} catch (Exception e) {
			System.exit(1);
		}
		System.exit(0);
		System.out.println("End...");
	}
}
